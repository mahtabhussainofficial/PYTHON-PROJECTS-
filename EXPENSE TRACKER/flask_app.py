from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"

# 🗄️ Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# 🏢 NAYA: Company Table (Har business ka apna record)
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='company', lazy=True)
    expenses = db.relationship('Expense', backref='company', lazy=True)

# 👤 User Table (Update: Ab user ki company aur role bhi save hoga)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # 'admin' ya 'staff'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)

# 💰 Expense Table (Update: Ab kharcha direct company se link hoga)
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    trans_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# 📧 --- EMAIL SENDER FUNCTION --- (Aapki original logic)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "mahtabhussainofficial@gmail.com"
SENDER_PASSWORD = "kguz ymjn fkca qopt"

def send_login_alert(user_name, user_email):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Security Alert: New Login"
        msg["From"] = SENDER_EMAIL
        msg["To"] = user_email
        html_content = f"<h3>Hello {user_name},</h3><p>New login detected to your Expense Tracker account.</p>"
        msg.attach(MIMEText(html_content, "html"))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email failed: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
        
    # NAYA JADOO: Ab sirf us user ke nahi, balkay uski poori Company ke expenses screen par aayenge!
    company_id = session['company_id']
    company_expenses = Expense.query.filter_by(company_id=company_id).order_by(Expense.id.desc()).all()
    
    total_income = sum(t.amount for t in company_expenses if t.trans_type == 'Income')
    total_expense = sum(t.amount for t in company_expenses if t.trans_type == 'Expense')
    balance = total_income - total_expense

    return render_template('index.html', 
                           transactions=company_expenses, 
                           balance=balance, 
                           income=total_income, 
                           expense=total_expense,
                           user_name=session['user_name'])

@app.route('/add', methods=['POST'])
def add_transaction():
    if 'user_id' not in session: return redirect('/login')
    
    date_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    new_expense = Expense(
        user_id=session['user_id'],
        company_id=session['company_id'], # Kharcha company ke account mein ja raha hai
        trans_type=request.form['type'],
        amount=float(request.form['amount']),
        category=request.form['category'],
        date=date_str
    )
    db.session.add(new_expense)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:trans_id>')
def delete_transaction(trans_id):
    if 'user_id' not in session: return redirect('/login')
    
    expense_to_delete = Expense.query.get_or_404(trans_id)
    
    # NAYA: Agar aap "Admin" hain to company ka koi bhi kharcha delete kar sakte hain
    if session['role'] == 'admin' and expense_to_delete.company_id == session['company_id']:
        db.session.delete(expense_to_delete)
        db.session.commit()
    # Lekin "Staff" sirf apne add kiye hue kharchay delete kar sakega
    elif expense_to_delete.user_id == session['user_id']:
        db.session.delete(expense_to_delete)
        db.session.commit()
        
    return redirect('/')

@app.route('/reset')
def reset_data():
    if 'user_id' not in session: return redirect('/login')
    
    # NAYA: Reset button sirf Admin daba sakta hai!
    if session['role'] == 'admin':
        Expense.query.filter_by(company_id=session['company_id']).delete()
        db.session.commit()
    else:
        flash("Action Denied: Only Admin can reset company data!")
        
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Pehle Nayi Company create ki
        # (Agle step mein hum HTML mein form field add karenge, abhi default 'My Business' hai)
        company_name = request.form.get('company_name', 'My Business') 
        new_company = Company(name=company_name)
        db.session.add(new_company)
        db.session.commit() # Save taake company ko ID mil jaye
        
        # 2. Phir User create kiya aur usay us company ka "Admin" bana diya
        hashed_password = generate_password_hash(request.form['password'])
        new_user = User(
            name=request.form['name'], 
            email=request.form['email'], 
            password=hashed_password,
            role='admin',
            company_id=new_company.id
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash("Company and Admin Account Created!")
        return redirect('/login')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['company_id'] = user.company_id # NAYA: Company ka link bhi yaad rakhna
            session['role'] = user.role             # NAYA: Role bhi yaad rakhna
            
            threading.Thread(target=send_login_alert, args=(user.name, user.email)).start()
            return redirect('/')
        else:
            flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    # 1. Security Check: Sirf Admin is page par aa sakta hai
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access Denied: Only Admins can add staff.")
        return redirect('/')
        
    if request.method == 'POST':
        # 2. Staff ka account banayen aur Admin wali Company mein hi jor dein
        hashed_password = generate_password_hash(request.form['password'])
        new_staff = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_password,
            role='staff', # NAYA: Isko Admin nahi, Staff ka role milega
            company_id=session['company_id'] # NAYA: Admin wali same company ID
        )
        db.session.add(new_staff)
        db.session.commit()
        
        return redirect('/')
        
    return render_template('add_staff.html')
if __name__ == '__main__':
    app.run(debug=True)