"""
Create post routes
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.item import Item
from app.models.item_image import ItemImage
from app.models.action_log import ActionLog
from app.services.ai_service import ai_detector
from app.services.ai_trainer import refresh_ai_model

bp = Blueprint('posts_create', __name__)

def allowed_file(filename):
    return '.' in filename

from datetime import datetime

@bp.route('/post', methods=['GET', 'POST'])
@login_required
def post_item():
    if request.method == 'POST':
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json'

        title = request.form.get('title')
        desc = request.form.get('description')
        location = request.form.get('location')
        specific_location = request.form.get('specific_location')
        category = request.form.get('category')
        itype = request.form.get('item_type')
        phone_number = request.form.get('phone_number')
        facebook_url = request.form.get('facebook_url')
        incident_date_str = request.form.get('incident_date')
        
        # Backward compatibility for contact_info column
        contact = f"SĐT: {phone_number}"
        if facebook_url:
            contact += f" | FB: {facebook_url}"

        incident_date = None
        if incident_date_str:
            try:
                incident_date = datetime.strptime(incident_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # AI Spam Check
        post_text = f"{title} {desc}"
        is_spam, score = ai_detector.is_spam(post_text)
        
        if is_spam:
            msg = f'Bài viết bị từ chối: Nội dung quá giống với bài viết đã có (Độ trùng lặp: {score:.2f}).'
            if is_ajax:
                return jsonify({'success': False, 'message': msg})
            flash(msg, 'warning')
            return render_template('posts/post_item.html', title=title, description=desc, location=location, contact_info=contact)

        new_item = Item(
            title=title, description=desc, location=location, specific_location=specific_location,
            category=category, item_type=itype, contact_info=contact, 
            phone_number=phone_number, facebook_url=facebook_url,
            incident_date=incident_date, user_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit() # Commit to get ID
        
        # Handle Image Uploads
        uploaded_files = request.files.getlist('images')
        saved_images = []
        upload_errors = []
        
        if uploaded_files:
            import cloudinary.uploader
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    try:
                        import cloudinary
                        import cloudinary.uploader
                        # Upload directly to Cloudinary
                        upload_result = cloudinary.uploader.upload(file, folder="flostfound/posts")
                        image_url = upload_result.get('secure_url')

                        img_obj = ItemImage(image_url=image_url, item_id=new_item.id)
                        db.session.add(img_obj)
                        saved_images.append(image_url)
                    except Exception as e:
                        err_msg = str(e)
                        print(f"Error uploading image to cloudinary: {err_msg}")
                        upload_errors.append(err_msg)

        # Set primary image
        if saved_images:
            new_item.image_url = saved_images[0]
            db.session.commit()

        # Log action
        log = ActionLog(user_id=current_user.id, action="Đăng bài", details=f"Tiêu đề: {title}")
        db.session.add(log)
        db.session.commit()
        
        # Update AI model with new data
        refresh_ai_model()
        
        if is_ajax:
            return jsonify({
                'success': True,
                'message': 'Đăng tin thành công!',
                'redirect_url': url_for('posts_view.index'),
                'item_id': new_item.id,
                'images_uploaded': len(saved_images),
                'upload_errors': upload_errors  # Show errors in browser DevTools
            })
            
        flash('Đăng tin thành công!', 'success')
        return redirect(url_for('posts_view.index'))
        
    return render_template('posts/post_item.html')
