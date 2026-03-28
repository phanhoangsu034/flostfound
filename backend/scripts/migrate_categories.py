
import os
import sys

# Thêm đường dẫn backend vào sys.path để có thể import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.item import Item
from app.models.category import Category

def migrate():
    app = create_app()
    with app.app_context():
        # 1. Định nghĩa các danh mục chuẩn
        standard_categories = [
            "Ví tiền",
            "Giấy tờ",
            "Điện thoại",
            "Laptop",
            "Chìa khóa",
            "Trang phục",
            "Khác"
        ]
        
        # 2. Tạo danh mục nếu chưa có
        category_map = {}
        for cat_name in standard_categories:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
                db.session.commit()
                print(f"Bổ sung danh mục: {cat_name}")
            category_map[cat_name] = cat
            
        # 3. Ánh xạ các bài đăng cũ
        items = Item.query.all()
        migrated_count = 0
        for item in items:
            # Nếu item chưa có categories nào gắn vào
            if item.categories.count() == 0 and item.category:
                # Tìm danh mục tương ứng (xử lý case-insensitive hoặc mapping nếu cần)
                cat_name = item.category
                if cat_name in category_map:
                    item.categories.append(category_map[cat_name])
                    migrated_count += 1
                else:
                    # Nếu là loại khác không có trong map, gán vào "Khác"
                    item.categories.append(category_map["Khác"])
                    migrated_count += 1
        
        db.session.commit()
        print(f"Hoàn tất migrate {migrated_count} bài đăng sang hệ thống Multi-Category mới.")

if __name__ == "__main__":
    migrate()
