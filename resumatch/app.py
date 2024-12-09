# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from evaluations.evaluator import evaluate_resume
from database.models import (
    init_db,
    add_interviewee,
    get_all_interviewees,
    get_interviewee_by_id,
    update_interviewee,
    delete_interviewee_by_id
)
from utils.emailer import send_email
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')  # Use a secure secret key

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin123'

# Initialize the database at application startup
init_db()

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator to protect admin routes
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access this page.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Resume Upload Page
@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        
        uploaded_file = request.files['resume']
        
        if uploaded_file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(resume_path)

            try:
                # Evaluate the resume
                evaluation_results = evaluate_resume(resume_path)
                # Unpack evaluation results
                applicant_info, qualification_grade, skills_score, education_score, experience_score = evaluation_results

                # Get the applicant's name and email
                applicant_name = applicant_info.get('name', 'Applicant')
                recipient_email = applicant_info.get('email', '')

                if not recipient_email:
                    flash(f"No email found for applicant from resume {filename}")
                    return redirect(url_for('index'))

                # Determine if the applicant is accepted for an interview
                accepted = qualification_grade >= 70  # Threshold can be adjusted

                # Add to interviewees with all evaluation scores
                add_interviewee(
                    applicant_info=applicant_info,
                    qualification_grade=qualification_grade,
                    skills_score=skills_score,
                    education_score=education_score,
                    experience_score=experience_score,
                    status='Accepted' if accepted else 'Rejected'
                )

                # Send email to the applicant
                send_email(
                    recipient_email=recipient_email,
                    accepted=accepted,
                    qualification_grade=qualification_grade,
                    skills_score=skills_score,
                    education_score=education_score,
                    experience_score=experience_score,
                    applicant_name=applicant_name
                )

                flash('Resume successfully uploaded and processed. A confirmation email has been sent.')
                return redirect(url_for('thank_you'))

            except Exception as e:
                print(f"Error processing resume {filename}: {e}")
                flash(f"An error occurred while processing your resume: {e}")
                return redirect(request.url)

        else:
            flash('Allowed file types are pdf, docx, doc')
            return redirect(request.url)
    return render_template('upload.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Thank You Page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check credentials
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(request.url)
    return render_template('admin_login.html')

# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.')
    return redirect(url_for('admin_login'))

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    # Fetch all interviewees from the database
    interviewees = get_all_interviewees()
    return render_template('admin_dashboard.html', interviewees=interviewees)

# Edit Interviewee
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@admin_login_required
def edit_interviewee(id):
    interviewee = get_interviewee_by_id(id)
    if not interviewee:
        flash('Interviewee not found.')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Update interviewee details
        updated_info = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'status': request.form.get('status')
        }
        update_interviewee(id, updated_info)
        flash('Interviewee information updated successfully.')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_interviewee.html', interviewee=interviewee)

# Delete Interviewee
@app.route('/admin/delete/<int:id>', methods=['POST'])
@admin_login_required
def delete_interviewee(id):
    delete_interviewee_by_id(id)
    flash('Interviewee deleted successfully.')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)