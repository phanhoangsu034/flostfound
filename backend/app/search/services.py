"""
Search & Filter business logic.
Handles fuzzy matching, synonym expansion, filtering, sorting, and pagination.
"""
from difflib import SequenceMatcher
from sqlalchemy import or_, func
from app.models.item import Item
from app.search.synonyms import expand_query


# ---------------------------------------------------------------------------
# Fuzzy helpers
# ---------------------------------------------------------------------------

def _fuzzy_ratio(a: str, b: str) -> float:
    """Return similarity ratio (0.0 – 1.0) between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _text_contains_any(text: str, terms: list[str], fuzzy_threshold: float = 0.65) -> tuple[bool, float]:
    """
    Check if *text* contains (or fuzzy-matches) any of the *terms*.
    Returns (matched: bool, best_score: float).
    """
    text_lower = text.lower()
    best = 0.0
    for term in terms:
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

        # Also get ALL items passing hard filters for fuzzy fallback
        all_hard_filtered = q.all()

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
        else:
            q = q.order_by(Item.date_posted.desc())

        total = q.count()
        start = (page - 1) * per_page
        page_items = q.offset(start).limit(per_page).all()

    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        "items": [item.to_dict() for item in page_items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
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
    Return distinct locations grouped hierarchically:
    [{ "name": "Alpha", "sub_locations": ["Phòng 101", "Phòng 201", ...] }, ...]
    """
    items = Item.query.with_entities(
        Item.location, Item.specific_location
    ).distinct().all()

    loc_map = {}
    for loc, sub in items:
        if not loc:
            continue
        loc_key = loc.strip()
        if loc_key not in loc_map:
            loc_map[loc_key] = set()
        if sub and sub.strip():
            loc_map[loc_key].add(sub.strip())

    return [
        {"name": name, "sub_locations": sorted(list(subs))}
        for name, subs in sorted(loc_map.items())
    ]


def get_categories():
    """Return list of distinct category names from items."""
    from app.models.category import Category
    cats = Category.query.order_by(Category.name).all()
    if cats:
        return [c.name for c in cats]
    # Fallback: distinct categories from items
    rows = Item.query.with_entities(Item.category).distinct().all()
    return sorted([r[0] for r in rows if r[0]])
