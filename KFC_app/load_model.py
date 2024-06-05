from transformers import BertForSequenceClassification, BertTokenizer
import torch
# Load the saved model
loaded_model = BertForSequenceClassification.from_pretrained('/home/anhtuanuser/Documents/Hang_khoa_luan/model')
# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Text for prediction
example_text = input("Nhập nội dung câu hỏi: ")
# Món ăn rất tuyệt vời

# Tokenize the example text
inputs = tokenizer(example_text, return_tensors="pt")
# Make a prediction
with torch.no_grad():
    outputs = loaded_model(**inputs)
# Get the predicted label
predicted_label = torch.argmax(outputs.logits).item()
labels_array = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
# Print the predicted label
label_value = labels_array[predicted_label]
print(f"Predicted Label: {label_value}")