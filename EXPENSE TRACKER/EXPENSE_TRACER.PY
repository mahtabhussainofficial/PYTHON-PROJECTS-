import json
import os
from datetime import datetime

FILE_NAME = "expenses_data.json"

# --- File Handling ---
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    # Agar file nahi hai to hum ek empty structure return karenge
    return {"transactions": []}

def save_data(data):
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file, indent=4)

# --- Features ---

def add_transaction(data, trans_type):
    amount = float(input(f"Enter {trans_type} amount: Rs. "))
    
    if trans_type == "Expense":
        print("Categories: Food, Transport, Bills, Entertainment, Shopping, Other")
    else:
        print("Categories: Salary, Freelance, Gift, Other")
        
    category = input("Enter Category: ").title()
    description = input("Enter brief description (optional): ")
    
    # Automatically aaj ki date aur time save karna
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    transaction = {
        "type": trans_type,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date_str
    }
    
    data["transactions"].append(transaction)
    save_data(data)
    print(f"{trans_type} of Rs. {amount} added successfully!\n")

def view_summary(data):
    total_income = 0
    total_expense = 0
    
    for t in data["transactions"]:
        if t["type"] == "Income":
            total_income += t["amount"]
        elif t["type"] == "Expense":
            total_expense += t["amount"]
            
    balance = total_income - total_expense
    
    print("\n" + "="*30)
    print(" FINANCIAL SUMMARY")
    print("="*30)
    print(f"Total Income:    Rs. {total_income}")
    print(f"Total Expenses:  Rs. {total_expense}")
    print("-" * 30)
    
    if balance >= 0:
        print(f"Remaining Bal:   Rs. {balance} (In Profit)")
    else:
        print(f"Remaining Bal:   Rs. {balance} (In Loss) ")
    print("="*30 + "\n")

def filter_expenses(data):
    print("\n--- Filter Expenses ---")
    category_to_search = input("Enter Category to search (e.g., Food, Transport): ").title()
    
    found = False
    total_for_category = 0
    
    print(f"\n--- Expenses for '{category_to_search}' ---")
    for t in data["transactions"]:
        if t["type"] == "Expense" and t["category"] == category_to_search:
            print(f"Date: {t['date']} | Amount: Rs. {t['amount']} | Desc: {t['description']}")
            total_for_category += t["amount"]
            found = True
            
    if found:
        print("-" * 30)
        print(f"Total spent on {category_to_search}: Rs. {total_for_category}\n")
    else:
        print(" No expenses found for this category.\n")

def view_all(data):
    if not data["transactions"]:
        print("No transactions recorded yet!\n")
        return
        
    print("\n--- All Transactions ---")
    for t in data["transactions"]:
        indicator = "+" if t["type"] == "Income" else "-"
        print(f"[{t['date']}] {indicator} Rs. {t['amount']} | {t['category']} ({t['description']})")
    print("-" * 30 + "\n")

# --- Main Program Loop ---
def main():
    data = load_data()
    
    while True:
        print("=== EXPENSE TRACKER ===")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Financial Summary (Balance)")
        print("4. Search/Filter Expenses by Category")
        print("5. View All Transactions")
        print("6. Exit")
        
        choice = input("Select an option (1-6): ")
        
        if choice == '1':
            add_transaction(data, "Income")
        elif choice == '2':
            add_transaction(data, "Expense")
        elif choice == '3':
            view_summary(data)
        elif choice == '4':
            filter_expenses(data)
        elif choice == '5':
            view_all(data)
        elif choice == '6':
            print("Data Saved. Good bye!")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()