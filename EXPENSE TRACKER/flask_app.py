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

# 👤 User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True) # User ke expenses link karna

# 💰 Expense Table (Naya Table)
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trans_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# 📧 --- EMAIL SENDER FUNCTION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "mahtabhussainofficial@gmail.com"        # 👉 YAHAN APNI GMAIL LIKHEIN
SENDER_PASSWORD = "kguz ymjn fkca qopt" # 👉 YAHAN 16-DIGIT APP PASSWORD LIKHEIN

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
        
    # Sirf us user ke expenses lao jo login hai
    user_id = session['user_id']
    user_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.id.desc()).all()
    
    # Dashboard Calculations
    total_income = sum(t.amount for t in user_expenses if t.trans_type == 'Income')
    total_expense = sum(t.amount for t in user_expenses if t.trans_type == 'Expense')
    balance = total_income - total_expense

    return render_template('index.html', 
                           transactions=user_expenses, 
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
    # Check karein ke delete karne wala apna hi data delete kar raha hai
    if expense_to_delete.user_id == session['user_id']:
        db.session.delete(expense_to_delete)
        db.session.commit()
    return redirect('/')

# 🆕 Reset Data Route
@app.route('/reset')
def reset_data():
    if 'user_id' not in session: return redirect('/login')
    
    # User ke tamam expenses delete kar do
    Expense.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return redirect('/')

# Auth Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])
        new_user = User(name=request.form['name'], email=request.form['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['user_name'] = user.name
            threading.Thread(target=send_login_alert, args=(user.name, user.email)).start()
            return redirect('/')
        else:
            flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)