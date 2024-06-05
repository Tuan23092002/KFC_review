from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
from transformers import BertForSequenceClassification, BertTokenizer
import torch

app = Flask(__name__)

# Load the model and tokenizer once at the beginning
model_path = '/home/anhtuanuser/Documents/KFC_app/model/'
loaded_model = None
tokenizer = None

@app.route('/load_model', methods=['GET'])
def load_model():
    global loaded_model, tokenizer
    try:
        loaded_model = BertForSequenceClassification.from_pretrained(model_path)
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        return "Model loaded successfully!", 200
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return render_template('review.html')

def save_review(reviewer, location, service, staff, food, drinks, comment, predicted_label):
    # Kết nối đến cơ sở dữ liệu (hoặc tạo mới nếu chưa có)
    conn = sqlite3.connect('reviews.db')

    # Tạo một đối tượng cursor để thực thi các câu lệnh SQL
    cursor = conn.cursor()

    # Lấy ngày hiện tại
    review_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Thêm đánh giá vào bảng 'reviews'
    cursor.execute('''
    INSERT INTO reviews (reviewer, location, service_rating, staff_rating, food_rating, drinks_rating, comment, review_date, predicted_label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (reviewer, location, service, staff, food, drinks, comment, review_date, predicted_label))

    # Xác nhận thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    

def predict_label(comment):
    """
    Hàm dự đoán nhãn của một đánh giá dựa trên comment.

    Args:
    comment (str): Nội dung của đánh giá.

    Returns:
    str: Nhãn dự đoán (Positive, Neutral, Negative).
    """
    if loaded_model is None or tokenizer is None:
        raise ValueError("Model and tokenizer are not loaded.")
    
    # Tokenize the input comment
    inputs = tokenizer(comment, return_tensors="pt")
    
    # Make a prediction
    with torch.no_grad():
        outputs = loaded_model(**inputs)
    
    # Get the predicted label
    predicted_label = torch.argmax(outputs.logits).item()
    labels_array = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    
    # Return the predicted label
    return labels_array[predicted_label]

@app.route('/submit', methods=['POST'])
def submit_review():
    reviewer = request.form['reviewer']
    location = request.form['location']
    service = int(request.form['service'])
    staff = int(request.form['staff'])
    food = int(request.form['food'])
    drinks = int(request.form['drinks'])
    comment = request.form['comment']
    
    # Dự đoán nhãn cho comment
    predicted_label = predict_label(comment)
    
    # Lưu đánh giá vào cơ sở dữ liệu
    save_review(reviewer, location, service, staff, food, drinks, comment, predicted_label)
    
    # Chuẩn bị dữ liệu để trả về cho trang kết quả
    result = {
        "reviewer": reviewer,
        "location": location,
        "service": service,
        "staff": staff,
        "food": food,
        "drinks": drinks,
        "comment": comment,
        "predicted_label": predicted_label
    }
    
    return render_template('result.html', result=result)

@app.route('/comments')
def view_comments():
    sort_order = request.args.get('sort', 'newest')
    label_filter = request.args.get('label', 'all')
    location_filter = request.args.get('location', 'all')

    # Kết nối đến cơ sở dữ liệu
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()

    query = 'SELECT reviewer, location, service_rating, staff_rating, food_rating, drinks_rating, comment, review_date, predicted_label FROM reviews'
    filters = []
    if label_filter != 'all':
        filters.append(f"predicted_label = '{label_filter}'")
    if location_filter != 'all':
        filters.append(f"location = '{location_filter}'")
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    
    if sort_order == 'newest':
        query += ' ORDER BY review_date DESC'
    elif sort_order == 'oldest':
        query += ' ORDER BY review_date ASC'

    cursor.execute(query)
    reviews = cursor.fetchall()
    conn.close()

    return render_template('comments.html', reviews=reviews)

if __name__ == '__main__':
    # Ensure the model is loaded before starting the server
    with app.app_context():
        load_model()
    app.run(debug=True)
