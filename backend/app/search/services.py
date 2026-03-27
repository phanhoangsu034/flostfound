"""
Search & Filter business logic.
Handles fuzzy matching, synonym expansion, filtering, sorting, and pagination.
"""
from difflib import SequenceMatcher
import unicodedata
from datetime import datetime, timedelta
from sqlalchemy import or_, func, desc
from app.models.item import Item
from app.models.like import Like
from app.models.comment import Comment
from app.extensions import db
from app.search.synonyms import expand_query


# ---------------------------------------------------------------------------
# Fuzzy helpers
# ---------------------------------------------------------------------------

def remove_accents(input_str: str) -> str:
    """Remove Vietnamese accents for robust searching."""
    if not input_str:
        return ""
    # Normalize unicode characters
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Keep only non-combining characters
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def _fuzzy_ratio(a: str, b: str) -> float:
    """Return similarity ratio (0.0 – 1.0) between two strings."""
    return SequenceMatcher(None, remove_accents(a.lower()), remove_accents(b.lower())).ratio()


def _text_contains_any(text: str, terms: list[str], fuzzy_threshold: float = 0.65) -> tuple[bool, float]:
    """
    Check if *text* contains (or fuzzy-matches) any of the *terms*.
    Returns (matched: bool, best_score: float).
    """
    text_lower = remove_accents(text.lower())
    terms_normalized = [remove_accents(t.lower()) for t in terms]
    best = 0.0
    for term in terms_normalized:
        # Exact substring match → perfect score
        if term in text_lower:
            return True, 1.0
        # Fuzzy match against each word in text
        for word in text_lower.split():
            ratio = _fuzzy_ratio(term, word)
            if ratio > best:
                best = ratio
    return best >= fuzzy_threshold, best


# ---------------------------------------------------------------------------
# Core search
# ---------------------------------------------------------------------------

def search_items(
    query: str = "",
    item_type: str = "",        # "Lost" | "Found" | ""
    status: str = "",           # "Open" | "Closed" | ""
    location: str = "",         # Building / area
    specific_location: str = "",# Room / floor
    category: str = "",
    date_range: str = "",       # "today" | "3days" | "7days" | "30days"
    sort: str = "newest",       # "newest" | "oldest" | "relevance"
    page: int = 1,
    per_page: int = 12,
):
    """
    Main search function.  Returns dict with items list, total, pages, etc.
    """
    # --- Start with base query ---
    q = Item.query

    # --- Hard filters (always exact match) ---
    if item_type:
        q = q.filter(Item.item_type == item_type)

    if status:
        q = q.filter(Item.status == status)
    else:
        # Default: hide closed/returned items
        q = q.filter(Item.status == "Open")

    if location:
        q = q.filter(func.lower(Item.location) == location.lower())

    if specific_location:
        q = q.filter(func.lower(Item.specific_location) == specific_location.lower())

    if category:
        q = q.filter(func.lower(Item.category) == category.lower())

    if date_range:
        now = datetime.utcnow()
        if date_range == "today":
            cutoff = now - timedelta(days=1)
        elif date_range == "3days":
            cutoff = now - timedelta(days=3)
        elif date_range == "7days":
            cutoff = now - timedelta(days=7)
        elif date_range == "30days":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None

        if cutoff:
            q = q.filter(or_(Item.date_posted >= cutoff, Item.incident_date >= cutoff))

    # --- Text search (fuzzy + synonym expansion) ---
    if query.strip():
        expanded_terms = expand_query(query)

        # Build OR conditions for each term
        or_conditions = []
        for term in expanded_terms:
            like_pattern = f"%{term}%"
            or_conditions.append(func.lower(Item.title).like(like_pattern))
            or_conditions.append(func.lower(Item.description).like(like_pattern))
            or_conditions.append(func.lower(Item.location).like(like_pattern))

        # Get candidate items matching DB-level LIKE
        db_items = q.filter(or_(*or_conditions)).all() if or_conditions else []

        # Also get a limited fallback list for fuzzy matching instead of all()
        # Fallback to the latest 200 items that match hard filters to prevent loading all into RAM
        all_hard_filtered = q.order_by(Item.date_posted.desc()).limit(200).all()

        # Merge: DB matches + fuzzy matches from remaining items
        seen_ids = {item.id for item in db_items}
        fuzzy_extras = []
        for item in all_hard_filtered:
            if item.id in seen_ids:
                continue
            # Check fuzzy against title and description
            combined_text = f"{item.title} {item.description} {item.location}"
            matched, _ = _text_contains_any(combined_text, expanded_terms, fuzzy_threshold=0.65)
            if matched:
                fuzzy_extras.append(item)
                seen_ids.add(item.id)

        all_matched = db_items + fuzzy_extras

        # Score each item for relevance sorting
        scored = []
        for item in all_matched:
            score = 0.0
            combined = f"{item.title} {item.description} {item.location}"
            for term in expanded_terms:
                _, ratio = _text_contains_any(combined, [term])
                # Title matches worth more
                if term in item.title.lower():
                    score += 3.0
                elif term in item.description.lower():
                    score += 1.5
                elif term in item.location.lower():
                    score += 1.0
                score += ratio
            scored.append((item, score))

        # Sort
        if sort == "oldest":
            scored.sort(key=lambda x: x[0].date_posted)
        elif sort == "relevance":
            scored.sort(key=lambda x: x[1], reverse=True)
        elif sort == "popular":
            # Sort by total interactions (likes + comments) descending
            def _interaction_count(item):
                lc = item.likes.count() if hasattr(item, 'likes') else 0
                cc = item.comments.count() if hasattr(item, 'comments') else 0
                return lc + cc
            scored.sort(key=lambda x: _interaction_count(x[0]), reverse=True)
        else:  # newest (default)
            scored.sort(key=lambda x: x[0].date_posted, reverse=True)

        total = len(scored)
        start = (page - 1) * per_page
        end = start + per_page
        page_items = [item for item, _ in scored[start:end]]

    else:
        # No text query – just filters + sort
        if sort == "oldest":
            q = q.order_by(Item.date_posted.asc())
        elif sort == "popular":
            # Subquery: count likes per item
            like_count = (
                db.session.query(Like.item_id, func.count(Like.id).label('lc'))
                .group_by(Like.item_id).subquery()
            )
            # Subquery: count comments per item
            comment_count = (
                db.session.query(Comment.item_id, func.count(Comment.id).label('cc'))
                .group_by(Comment.item_id).subquery()
            )
            q = (
                q.outerjoin(like_count, Item.id == like_count.c.item_id)
                .outerjoin(comment_count, Item.id == comment_count.c.item_id)
                .order_by(
                    desc(func.coalesce(like_count.c.lc, 0) + func.coalesce(comment_count.c.cc, 0)),
                    Item.date_posted.desc()
                )
            )
        else:
            q = q.order_by(Item.date_posted.desc())

        total = q.count()
        start = (page - 1) * per_page
        page_items = q.offset(start).limit(per_page).all()

    total_pages = max(1, (total + per_page - 1) // per_page)

    # Dynamic counts for Lost and Found items matching current non-type query
    # (Excluding item_type filter so we can show counts for both tabs)
    count_q = Item.query
    if status:
        count_q = count_q.filter(Item.status == status)
    else:
        count_q = count_q.filter(Item.status == "Open")
    if location: count_q = count_q.filter(func.lower(Item.location) == location.lower())
    if specific_location: count_q = count_q.filter(func.lower(Item.specific_location) == specific_location.lower())
    if category: count_q = count_q.filter(func.lower(Item.category) == category.lower())
    if 'cutoff' in locals() and cutoff:
        count_q = count_q.filter(or_(Item.date_posted >= cutoff, Item.incident_date >= cutoff))

    lost_count = count_q.filter(Item.item_type == 'Lost').count()
    found_count = count_q.filter(Item.item_type == 'Found').count()

    return {
        "items": [item.to_dict() for item in page_items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "counts": {
            "lost": lost_count,
            "found": found_count
        }
    }


# ---------------------------------------------------------------------------
# Autocomplete
# ---------------------------------------------------------------------------

def autocomplete(query: str, max_keywords: int = 5, max_items: int = 3):
    """
    Returns keyword suggestions + quick-match items for the autocomplete
    dropdown (called on every keystroke with debounce).
    """
    if not query.strip():
        return {"keywords": [], "items": []}

    expanded = expand_query(query)

    # Keyword suggestions = expanded terms that are different from the query
    keyword_suggestions = [t for t in expanded if t.lower() != query.lower().strip()][:max_keywords]

    # Quick-match items
    or_conditions = []
    for term in expanded:
        like_pattern = f"%{term}%"
        or_conditions.append(func.lower(Item.title).like(like_pattern))
        or_conditions.append(func.lower(Item.description).like(like_pattern))

    quick_items = []
    if or_conditions:
        quick_items = (
            Item.query
            .filter(Item.status == "Open")
            .filter(or_(*or_conditions))
            .order_by(Item.date_posted.desc())
            .limit(max_items)
            .all()
        )

    return {
        "keywords": keyword_suggestions,
        "items": [item.to_dict() for item in quick_items],
    }


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def get_locations_hierarchy():
    """
    Return static hierarchical location list for FPTU.
    """
    return [
        {"name": "Tòa nhà", "sub_locations": ["Alpha", "Beta", "Delta", "Epsilon", "Gamma"]},
        {"name": "Canteen", "sub_locations": ["Canteen 1", "Canteen 2"]},
        {"name": "Dọc đường 30m", "sub_locations": []},
        {"name": "Dom", "sub_locations": ["Dom A", "Dom B", "Dom C", "Dom D", "Dom E", "Dom F", "Dom G", "Dom H", "Dom I"]},
        {"name": "Sân bóng", "sub_locations": ["Sân bóng 1", "Sân bóng 2", "Sân bóng 3"]},
        {"name": "Nhà xe", "sub_locations": []},
        {"name": "Hồ", "sub_locations": ["Hồ tình yêu", "Hồ thiên nga"]},
        {"name": "Khác", "sub_locations": []}
    ]


def get_categories():
    """Return list of category names ensuring standard ones are present."""
    from app.models.category import Category
    
    # Danh sách chuẩn khớp với frontend
    standard_cats = [
        "Ví tiền",
        "Giấy tờ",
        "Điện thoại",
        "Laptop",
        "Chìa khóa",
        "Trang phục",
        "Khác"
    ]
    
    # Cố gắng lấy từ DB để có thể có các category người dùng đã tạo thêm tự động
    db_cats = []
    try:
        cats = Category.query.all()
        db_cats = [c.name for c in cats]
    except Exception:
        pass
        
    # Gộp danh sách chuẩn và DB, giữ thứ tự chuẩn lên trước
    merged_cats = standard_cats.copy()
    for cat in db_cats:
        if cat not in merged_cats:
            merged_cats.append(cat)
            
    return merged_cats
