import sqlite3
from datetime import datetime

# Kết nối đến cơ sở dữ liệu (hoặc tạo mới nếu chưa có)
conn = sqlite3.connect('reviews.db')

# Tạo một đối tượng cursor để thực thi các câu lệnh SQL
cursor = conn.cursor()

# Tạo bảng 'reviews' với các thuộc tính được chỉ định
cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer TEXT NOT NULL,
    location TEXT NOT NULL,
    service_rating INTEGER NOT NULL,
    staff_rating INTEGER NOT NULL,
    food_rating INTEGER NOT NULL,
    drinks_rating INTEGER NOT NULL,
    comment TEXT,
    review_date TEXT,
    predicted_label TEXT
)
''')

# Định nghĩa giá trị cho ngày đánh giá và nhãn dự đoán
review_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
predicted_label = 'Negative'  # Ví dụ nhãn dự đoán

# Thêm đánh giá vào bảng 'reviews'
cursor.execute('''
INSERT INTO reviews (reviewer, location, service_rating, staff_rating, food_rating, drinks_rating, comment, review_date, predicted_label)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Tuan', 'KFC Sơn Tây', 1, 1, 1, 1, 'hihi', review_date, predicted_label))

# Xác nhận thay đổi
conn.commit()

# Đóng kết nối
conn.close()
