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
