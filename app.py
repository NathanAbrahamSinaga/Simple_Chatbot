from flask import Flask, render_template, request, jsonify
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

app = Flask(__name__)

model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'model', 'chat_model_final'))

try:
    if not os.path.exists(model_path):
        raise OSError(f"Model directory not found at {model_path}")
    
    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id
    print(f"Model successfully loaded from: {model_path}")
    
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print("Falling back to default GPT2 model")
    tokenizer = GPT2Tokenizer.from_pretrained('indonesian-nlp/gpt2')
    model = GPT2LMHeadModel.from_pretrained('indonesian-nlp/gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id

def generate_response(prompt, max_length=300):
    encoded_input = tokenizer.encode_plus(
        prompt,
        return_tensors='pt',
        padding=True,
        truncation=True,
        max_length=max_length,
        return_attention_mask=True
    )
    
    outputs = model.generate(
        input_ids=encoded_input['input_ids'],
        attention_mask=encoded_input['attention_mask'],
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    response = generate_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)