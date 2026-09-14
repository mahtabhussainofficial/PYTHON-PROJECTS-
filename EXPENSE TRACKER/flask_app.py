from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime
import uuid # Har transaction ko ek unique ID dene ke liye

app = Flask(__name__)
FILE_NAME = "expenses_data.json"

def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    return {"transactions": []}

def save_data(data):
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def home():
    data = load_data()
    transactions = data["transactions"]
    
    # Dashboard Calculations
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
    balance = total_income - total_expense
    
    # 🔍 SEARCH / FILTER LOGIC
    search_query = request.args.get('search_query', '')
    if search_query:
        # Agar user ne kuch search kiya hai, to sirf wahi category filter karein
        display_list = [t for t in transactions if search_query.lower() in t['category'].lower()]
    else:
        display_list = transactions
        
    display_list = list(reversed(display_list))

    return render_template('index.html', 
                           transactions=display_list, 
                           balance=balance, 
                           income=total_income, 
                           expense=total_expense,
                           search_query=search_query)

@app.route('/add', methods=['POST'])
def add_transaction():
    trans_type = request.form['type']
    amount = float(request.form['amount'])
    category = request.form['category']
    date_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    
    data = load_data()
    data["transactions"].append({
        "id": str(uuid.uuid4()), # 🆕 Real-world apps hamesha unique ID generate karti hain
        "type": trans_type,
        "amount": amount,
        "category": category,
        "date": date_str
    })
    save_data(data)
    
    return redirect('/')

# 🗑️ DELETE LOGIC
@app.route('/delete/<string:trans_id>')
def delete_transaction(trans_id):
    data = load_data()
    # List comprehension se wo transaction nikal dein jiski ID match ho jaye
    data["transactions"] = [t for t in data["transactions"] if t.get('id') != trans_id]
    save_data(data)
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)