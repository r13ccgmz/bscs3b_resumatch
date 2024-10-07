from flask import Flask, render_template, request, redirect, url_for
from evaluations.evaluator import evaluate_resume
from database.models import add_interviewee, init_db
from utils.emailer import send_email

app = Flask(__name__)

# Initialize the database at application startup
init_db()

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Resume Upload Page
@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        uploaded_file = request.files['resume']
        if uploaded_file.filename != '':
            # Save the uploaded resume
            resume_path = 'uploads/' + uploaded_file.filename
            uploaded_file.save(resume_path)

            # Evaluate the resume
            applicant_info, qualification_grade = evaluate_resume(resume_path)

            # Determine if the applicant is accepted for an interview
            if qualification_grade >= 75:  # Threshold can be adjusted
                add_interviewee(applicant_info)
                send_email(applicant_info['email'], accepted=True)
            else:
                send_email(applicant_info['email'], accepted=False)

            return redirect(url_for('thank_you'))
    return render_template('upload.html')

# Thank You Page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)