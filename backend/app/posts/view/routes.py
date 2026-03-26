"""
View posts routes (index/home page)
"""
from flask import Blueprint, render_template, request, jsonify
from app.models.item import Item

bp = Blueprint('posts_view', __name__)

@bp.route('/')
def index():
    query = request.args.get('q', '').strip()
    if query:
        items = Item.query.filter(
            (Item.title.contains(query)) | 
            (Item.description.contains(query)) |
            (Item.location.contains(query))
        ).order_by(Item.date_posted.desc()).all()
    else:
        items = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('posts/index.html', items=items, query=query)

@bp.route('/api/posts/<int:item_id>')
def get_post_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify({
        'success': True,
        'data': item.to_dict()
    })

@bp.route('/post/<int:item_id>')
def post_detail_page(item_id):
    """
    Public route to view a single post (for SEO and Social Sharing)
    """
    item = Item.query.get_or_404(item_id)
    return render_template('posts/detail.html', item=item)
