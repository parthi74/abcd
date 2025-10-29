from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Models (FIXED: __tablename__ for plural; FK to 'companies.id')
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON as string
    score = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # Store as string for +91
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

# Question sets
question_sets = {
    'startup': [
        "Do you have a clear business model?", "Do you have a team with diverse skills?",
        "Do you track your monthly burn rate?", "Do you use digital marketing?", "Do you have investor support?",
        "I am confident about scaling soon.", "Our market strategy is strong.",
        "We are growing faster than competitors.", "We have good cash flow.", "We are ready for long-term growth."
    ],
    'loss': [
        "Do you currently operate at a loss?", "Do you analyze your expenses monthly?",
        "Do you have debt obligations?", "Do you track profit/loss ratios?", "Do you face customer churn?",
        "We have clear recovery strategies.", "We control unnecessary costs.", "We maintain employee morale.",
        "We have strong management support.", "We plan for the next fiscal year carefully."
    ],
    'low': [
        "Is your profit margin below 10%?", "Do you track small improvements monthly?",
        "Do you rely on one major client?", "Do you face high operational costs?", "Do you plan to diversify revenue?",
        "We focus on long-term stability.", "Our cost structure is under control.", "We seek continuous improvement.",
        "We are adapting to market changes.", "We have a good customer base."
    ],
    'profit': [
        "Are your profit margins above 10%?", "Do you reinvest profits into growth?",
        "Do you have steady cash flow?", "Do you expand your customer base?", "Do you innovate regularly?",
        "We have sustainable operations.", "We maintain competitive advantage.", "We have high employee satisfaction.",
        "We plan to expand globally.", "We have great investor confidence."
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_category/<category>')
def select_category(category):
    if category in question_sets:
        session['selected_category'] = category
        return '', 204
    flash('Invalid category.')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('companyName')
    email = request.form.get('email')
    phone = request.form.get('phone')
    category = session.get('selected_category')

    if not all([name, email, phone, category]):
        flash('All fields are required.')
        return redirect(url_for('index'))

    if Company.query.filter_by(email=email).first():
        flash('Email already registered.')
        return redirect(url_for('survey'))

    company = Company(name=name, email=email, phone=phone, category=category)
    db.session.add(company)
    db.session.commit()
    session['company_id'] = company.id
    flash('Registration successful!')
    return redirect(url_for('survey'))

@app.route('/skip_login')
def skip_login():
    category = session.get('selected_category')
    if not category:
        flash('Please select a category first.')
        return redirect(url_for('index'))
    # Unique anonymous email
    anon_email = f'anonymous_{int(datetime.now().timestamp())}@amconnect.com'
    company = Company(name='Anonymous', email=anon_email, phone='N/A', category=category)
    db.session.add(company)
    db.session.commit()
    session['company_id'] = company.id
    return redirect(url_for('survey'))

@app.route('/survey')
def survey():
    category = session.get('selected_category')
    if not category:
        flash('Please select a category.')
        return redirect(url_for('index'))
    questions = question_sets[category]
    app.jinja_env.filters['enumerate'] = enumerate
    return render_template('survey.html', questions=questions, category=category)

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    category = session.get('selected_category')
    company_id = session.get('company_id')

    if not category or not company_id:
        flash('Session expired. Please start over.')
        return redirect(url_for('index'))

    # Validate company exists
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found. Please start over.')
        return redirect(url_for('index'))

    answers = {}
    score = 0

    # First 5: Yes/No
    for i in range(1, 6):
        ans = request.form.get(f'q{i}')
        if not ans:
            flash('Please answer all questions.')
            return redirect(url_for('survey'))
        answers[f'q{i}'] = ans
        if ans.lower() == 'yes':
            score += 10

    # Last 5: Agreement scale
    for i in range(6, 11):
        ans = request.form.get(f'q{i}')
        if not ans:
            flash('Please answer all questions.')
            return redirect(url_for('survey'))
        answers[f'q{i}'] = ans
        if ans == 'Strongly Agree':
            score += 10
        elif ans == 'Agree':
            score += 7
        elif ans == 'Intermediate':
            score += 5
        elif ans == 'Disagree':
            score += 2

    final_score = min(max(round((score / 100) * 100), 0), 100)

    survey = Survey(company_id=company_id, answers=json.dumps(answers), score=final_score)
    db.session.add(survey)
    db.session.commit()

    session['survey_score'] = final_score
    flash('Survey submitted successfully!')
    return redirect(url_for('result'))

@app.route('/result')
def result():
    score = session.get('survey_score', 0)
    if score == 0:
        flash('No survey completed.')
        return redirect(url_for('index'))

    circle_color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    msg = "✅ Great job! You don’t currently need our services." if score >= 75 else \
          "⚠️ You may benefit from our professional services." if score >= 50 else \
          "❌ You need our company services urgently!"

    return render_template('result.html', score=score, circle_color=circle_color, message=msg)

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        if not all([company_name, name, email, phone, message]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('contact_page'))

        # Optional: validate phone (basic)
        import re
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            flash('Please enter a valid phone number with country code.', 'error')
            return redirect(url_for('contact_page'))

        contact_entry = Contact(
            company_name=company_name,
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        db.session.add(contact_entry)
        db.session.commit()

        flash('Thank you! Your message has been sent successfully.', 'success')
        return redirect(url_for('contact_page'))

    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('aboutus.html')
@app.route('/services')
def services():
    return render_template('service.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Safe now with __tablename__
    app.run(debug=True)