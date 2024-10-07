import re
import os
import spacy
import docx2txt
from PyPDF2 import PdfReader
from collections import defaultdict

nlp = spacy.load('en_core_web_sm')

def extract_text_from_resume(resume_path):
    text = ''
    if resume_path.endswith('.pdf'):
        # Extract text from PDF
        reader = PdfReader(resume_path)
        for page in reader.pages:
            text += page.extract_text()
    elif resume_path.endswith('.docx') or resume_path.endswith('.doc'):
        # Extract text from DOCX/DOC
        text = docx2txt.process(resume_path)
    else:
        # Unsupported file type
        raise ValueError('Unsupported file type: {}'.format(resume_path))
    return text

def evaluate_resume(resume_path):
    text = extract_text_from_resume(resume_path)
    doc = nlp(text)

    # Extract applicant's information
    applicant_info = {
        'name': extract_name(doc),
        'email': extract_email(text),
        'phone': extract_phone_number(text),
    }

    # Extract sections
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)

    # Evaluate and score
    skills_score = score_skills(skills)
    education_score = score_education(education)
    experience_score = score_experience(experience)

    # Calculate total qualification grade
    qualification_grade = (skills_score + education_score + experience_score) / 3

    return applicant_info, qualification_grade

def extract_name(doc):
    # Use Named Entity Recognition to find person names
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return 'Applicant'

def extract_email(text):
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    return email[0] if email else ''

def extract_phone_number(text):
    phone = re.findall(r'\+?\d[\d\s-]{8,}\d', text)
    return phone[0] if phone else ''

def extract_skills(text):
    # List of desired skills
    desired_skills = [
        'python', 'java', 'machine learning', 'data analysis', 'communication',
        'project management', 'sql', 'javascript', 'react', 'leadership'
    ]
    skills_found = []
    for skill in desired_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            skills_found.append(skill.title())
    return skills_found

def score_skills(skills_found):
    # Assuming equal weight for each skill
    total_skills = 10  # Total number of desired skills
    score = (len(skills_found) / total_skills) * 100
    return min(score, 100)

def extract_education(text):
    # Degrees and Institutions Extraction
    degrees = ['Bachelor', 'Master', 'PhD', 'B\.Sc', 'M\.Sc', 'Bachelors', 'Masters', 'Doctorate']
    education = {'degree': '', 'institutions': []}
    for degree in degrees:
        if re.search(degree, text, re.IGNORECASE):
            education['degree'] = degree
            break
    # Extract institution names using NER
    doc = nlp(text)
    institutions = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    education['institutions'] = institutions
    return education

def score_education(education):
    degree_scores = {
        'PhD': 100,
        'Doctorate': 100,
        'Master': 80,
        'Masters': 80,
        'M.Sc': 80,
        'Bachelor': 60,
        'B.Sc': 60,
        'Bachelors': 60,
    }
    degree = education.get('degree', '')
    return degree_scores.get(degree, 0)

def extract_experience(text):
    # Experience Extraction based on years
    experience_years = 0
    patterns = [
        r'(\d+)\+?\s+years of experience',
        r'(\d+)\s+years\' experience',
        r'(\d+)-year experience',
        r'(\d+)\s+years experience'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            experience_years = int(match.group(1))
            break
    return {'years': experience_years}

def score_experience(experience):
    years = experience.get('years', 0)
    max_years = 10  # Max years to cap the score
    score = (years / max_years) * 100
    return min(score, 100)