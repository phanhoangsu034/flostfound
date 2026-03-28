"""
Search & Filter API routes.
Blueprint prefix: /api/search
"""
from flask import Blueprint, request, jsonify
from app.search.services import (
    search_items,
    autocomplete,
    get_locations_hierarchy,
    get_categories,
)

bp = Blueprint('search', __name__)


@bp.route('/api/search')
def api_search():
    """
    Main search + filter endpoint.
    Query params:
        q            – search text
        type         – Lost | Found
        status       – Open | Closed | all
        location     – building name
        sub_location – room / floor
        category     – category name
        sort         – newest | oldest | relevance
        page         – page number (default 1)
        per_page     – items per page (default 12)
    """
    q = request.args.get('q', '').strip()
    item_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    location = request.args.get('location', '').strip()
    sub_location = request.args.get('sub_location', '').strip()
    category = request.args.get('category', '').strip()
    date_range = request.args.get('date_range', '').strip()
    sort = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # "all" means don't filter by status
    if status == 'all':
        status = ''

    result = search_items(
        query=q,
        item_type=item_type,
        status=status,
        location=location,
        specific_location=sub_location,
        category=category,
        date_range=date_range,
        sort=sort,
        page=page,
        per_page=per_page,
    )
    return jsonify(result)


@bp.route('/api/search/autocomplete')
def api_autocomplete():
    """
    Autocomplete suggestions.
    Query params: q – search text
    """
    q = request.args.get('q', '').strip()
    result = autocomplete(q)
    return jsonify(result)


@bp.route('/api/search/locations')
def api_locations():
    """Return hierarchical location list."""
    return jsonify(get_locations_hierarchy())


@bp.route('/api/search/categories')
def api_categories():
    """Return category list."""
    return jsonify(get_categories())

from app.models.item import Item
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@bp.route('/api/search/match', methods=['POST'])
def api_search_match():
    """
    Search for similar items (matching 50% - 80%) for the create post suggestions.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    title = data.get('title', '').strip()
    desc = data.get('description', '').strip()
    item_type = data.get('item_type', '').strip()
    category = data.get('category', '').strip()

    if not title or not item_type:
        return jsonify({"success": True, "matches": []})

    opposite_type = 'Found' if item_type == 'Lost' else 'Lost'
    
    # Get candidates of opposite type that are Open
    # Use LIKE for category matching since categories can be comma-joined
    query = Item.query.filter_by(item_type=opposite_type, status='Open')
    
    if category:
        # Match any of the selected categories
        cat_list = [c.strip() for c in category.split(',')]
        from sqlalchemy import or_
        cat_filters = [Item.category.contains(c) for c in cat_list]
        query = query.filter(or_(*cat_filters))
    
    candidates = query.all()

    if not candidates:
        return jsonify({"success": True, "matches": []})

    texts = [f"{c.title} {c.description}" for c in candidates]
    new_text = f"{title} {desc}"

    try:
        vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
        tfidf_matrix = vectorizer.fit_transform(texts)
        new_vec = vectorizer.transform([new_text])
        cosine_sims = cosine_similarity(new_vec, tfidf_matrix)[0]
        
        # Sort indices descending
        top_indices = cosine_sims.argsort()[::-1]
        
        matches = []
        for idx in top_indices:
            sim = float(cosine_sims[idx])
            # Show matches with >= 15% similarity
            if sim >= 0.15:
                c = candidates[idx]
                
                # Determine primary image
                img_url = c.image_url
                if not img_url and c.images_list.count() > 0:
                    img_url = c.images_list[0].image_url
                
                matches.append({
                    "id": c.id,
                    "title": c.title,
                    "image_url": img_url,
                    "location": c.location,
                    "specific_location": c.specific_location,
                    "date_posted": c.date_posted.isoformat() + 'Z',
                    "sim_score": sim,
                    "user": c.user.username,
                    "item_type": c.item_type
                })
                
                if len(matches) >= 3:
                    break
        
        return jsonify({"success": True, "matches": matches})
    except Exception as e:
        print(f"Error in match search: {e}")
        return jsonify({"success": True, "matches": []})

