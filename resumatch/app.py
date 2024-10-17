from flask import Flask, render_template, request, redirect, url_for, flash
from evaluations.evaluator import evaluate_resume
from database.models import add_interviewee, init_db
from utils.emailer import send_email
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flashing messages

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database at application startup
init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                accepted = qualification_grade >= 75  # Threshold can be adjusted

                # Add to interviewees if accepted
                if accepted:
                    add_interviewee(applicant_info)

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

# Thank You Page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)