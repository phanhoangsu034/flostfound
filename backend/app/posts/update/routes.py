"""
Update post routes
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

bp = Blueprint('posts_update', __name__)

def allowed_file(filename):
    return '.' in filename

@bp.route('/post/status/<int:item_id>', methods=['POST'])
@login_required
def update_status(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    data = request.json
    if data and 'status' in data:
        item.status = data['status']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công'})
    return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400

@bp.route('/post/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Check ownership or admin
    if item.user_id != current_user.id and not current_user.is_admin:
        flash('Bạn không có quyền chỉnh sửa bài viết này.', 'danger')
        return redirect(url_for('posts_view.index'))

    if request.method == 'POST':
        # Handle AJAX/JSON requests vs Form submit
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        title = request.form.get('title')
        desc = request.form.get('description')
        location = request.form.get('location')
        specific_location = request.form.get('specific_location')
        category = request.form.get('category')
        itype = request.form.get('item_type')
        phone_number = request.form.get('phone_number')
        facebook_url = request.form.get('facebook_url')
        status = request.form.get('status', item.status)
        
        # Backward compatibility for contact_info column
        contact = f"SĐT: {phone_number}"
        if facebook_url:
            contact += f" | FB: {facebook_url}"
        
        inc_date_str = request.form.get('incident_date')
        if inc_date_str:
            from datetime import datetime
            try:
                # Value can be 'YYYY-MM-DDTHH:MM'
                item.incident_date = datetime.strptime(inc_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        item.title = title
        item.description = desc
        item.location = location
        item.specific_location = specific_location
        item.category = category
        item.item_type = itype
        item.contact_info = contact
        item.phone_number = phone_number
        item.facebook_url = facebook_url
        item.status = status
        
        # Handle deleted images
        deleted_images_json = request.form.get('deleted_images')
        if deleted_images_json:
            import json
            import cloudinary.uploader
            try:
                deleted_images = json.loads(deleted_images_json)
                print(f"[UPDATE] Deleting images: {deleted_images}")
                
                for img_url in deleted_images:
                    # Find and delete from database
                    img_obj = ItemImage.query.filter_by(image_url=img_url, item_id=item.id).first()
                    if img_obj:
                        db.session.delete(img_obj)
                        print(f"[UPDATE] Deleted image from DB: {img_url}")
                    
                    # Delete physical file
                    try:
                        if img_url.startswith('http'):
                            # Try to extract public_id to destroy from cloudinary
                            # e.g., https://res.cloudinary.com/.../image/upload/v.../folder/file.jpg
                            import re
                            parts = img_url.split('/upload/')
                            if len(parts) > 1:
                                path_after_upload = parts[1]
                                path_without_version = re.sub(r'^v\d+/', '', path_after_upload)
                                public_id = path_without_version.rsplit('.', 1)[0]
                            else:
                                public_id = img_url.split('/')[-1].split('.')[0]
                            cloudinary.uploader.destroy(public_id)
                            print(f"[UPDATE] Destroyed file in Cloudinary: {public_id}")
                        else:
                            file_path = os.path.join(current_app.static_folder, img_url)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"[UPDATE] Deleted local file: {file_path}")
                    except Exception as e:
                        print(f"[UPDATE] Error deleting file {img_url}: {e}")
            except Exception as e:
                print(f"[UPDATE] Error processing deleted_images: {e}")
        
        # Handle Image Uploads
        uploaded_files = request.files.getlist('images')
        
        # Process files
        new_images = []
        if uploaded_files:
            import cloudinary.uploader
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    try:
                        # Upload directly to Cloudinary
                        upload_result = cloudinary.uploader.upload(file, folder="flostfound/posts")
                        image_url = upload_result.get('secure_url')
                        
                        img_obj = ItemImage(image_url=image_url, item=item)
                        db.session.add(img_obj)
                        new_images.append(image_url)
                        print(f"[UPDATE] Added new image: {image_url}")
                    except Exception as e:
                        print(f"[UPDATE] Error uploading image to cloudinary: {e}")

        # Update primary image_url
        # Get all remaining images for this item
        all_images = ItemImage.query.filter_by(item_id=item.id).all()
        if all_images:
            # Set first image as primary
            item.image_url = all_images[0].image_url
            print(f"[UPDATE] Primary image set to: {item.image_url}")
        else:
            # No images left
            item.image_url = None
            print(f"[UPDATE] No images remaining, set to None")

        db.session.commit()
        print(f"[UPDATE] Update completed for item {item.id}")
        
        # Log action
        log = ActionLog(user_id=current_user.id, action="Cập nhật bài", details=f"ID: {item.id}")
        db.session.add(log)
        db.session.commit()
        
        if is_ajax:
             return jsonify({'success': True, 'message': 'Cập nhật thành công!'})
        
        flash('Cập nhật tin thành công!', 'success')
        return redirect(url_for('posts_view.index', new_post_id=item.id))
        
    return render_template('posts/post_item.html', item=item, is_edit=True)
