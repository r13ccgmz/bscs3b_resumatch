import re
import os
import spacy
import datetime
import docx2txt
from PyPDF2 import PdfReader
from collections import defaultdict
from fuzzywuzzy import fuzz

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_resume(resume_path):
    text = ''
    if resume_path.endswith('.pdf'):
        try:
            reader = PdfReader(resume_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
    elif resume_path.endswith('.docx') or resume_path.endswith('.doc'):
        try:
            text = docx2txt.process(resume_path)
        except Exception as e:
            raise ValueError(f"Error reading DOC/DOCX: {str(e)}")
    else:
        raise ValueError(f'Unsupported file type: {resume_path}')
    
    if not text.strip():
        raise ValueError("No text extracted from the resume.")
    
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
    education = extract_education(text)  # Enhanced education extraction
    experience = extract_experience(text)  # Enhanced experience extraction for developers

    # Evaluate and score
    skills_score = score_skills(skills)
    education_score = score_education(education)
    experience_score = score_experience(experience)

    # Calculate total qualification grade
    qualification_grade = (skills_score + education_score + experience_score) / 3

    return applicant_info, qualification_grade, skills_score, education_score, experience_score

def extract_name(doc):
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

# Enhanced skill extraction with synonyms and fuzzy matching
def extract_skills(text):
    skills_dict = {
        'python': ['python', 'py'],
        'java': ['java'],
        'machine learning': ['machine learning', 'ml'],
        'data analysis': ['data analysis', 'data analytics', 'analytics'],
        'communication': ['communication', 'interpersonal skills'],
        'project management': ['project management', 'pm'],
        'sql': ['sql', 'structured query language'],
        'javascript': ['javascript', 'js', 'java script'],
        'react': ['react', 'react.js', 'reactjs'],
        'leadership': ['leadership', 'team leader'],
        'version control': ['version control', 'git', 'svn', 'mercurial'],
        'problem solving': ['problem solving', 'critical thinking'],
        'api': ['api', 'application programming interface'],
        'c++': ['c++', 'cpp'],
        'database management': ['database management', 'dbms'],
        'Node.js': ['node.js', 'nodejs', 'node'],
        'analytical': ['analytical', 'analysis', 'critical thinking']
    }

    skills_found = []
    
    for skill, synonyms in skills_dict.items():
        for synonym in synonyms:
            pattern = rf'\b{re.escape(synonym)}\b'
            if re.search(pattern, text, re.IGNORECASE) or fuzz.partial_ratio(synonym.lower(), text.lower()) > 80:
                skills_found.append(skill.title())
                break
    
    return skills_found

def score_skills(skills_found):
    total_skills = 10
    score = (len(skills_found) / total_skills) * 100
    return min(score, 100)

# Enhanced education extraction
def extract_education(text):
    degrees_patterns = [
        r'Bachelor\'s Degree in (?:Computer Science|Information Technology|Software Engineering)',
        r'Bachelor in (?:Computer Science|Information Technology|Software Engineering)',
        r'Bachelor of Science in (?:Computer Science|Information Technology|Software Engineering)',
        r'Master\'s Degree in (?:Computer Science|Information Technology|Software Engineering)',
        r'Master in (?:Computer Science|Information Technology|Software Engineering)',
        r'PhD in (?:Computer Science|Information Technology|Software Engineering)',
        r'B\.Sc\.? (?:Computer Science|Information Technology|Software Engineering)',
        r'M\.Sc\.? (?:Computer Science|Information Technology|Software Engineering)',
        r'Doctorate in (?:Computer Science|Information Technology|Software Engineering)',
        r'Bachelors in (?:Computer Science|Information Technology|Software Engineering)',
        r'Masters in (?:Computer Science|Information Technology|Software Engineering)',
    ]

    education = {'degrees': [], 'institutions': []}
    
    for pattern in degrees_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education['degrees'].extend(matches)

    doc = nlp(text)
    institutions = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    education['institutions'] = institutions
    return education

def score_education(education):
    degree_scores = {
        'PhD in Computer Science': 100,
        'PhD in Information Technology': 100,
        'PhD in Software Engineering': 100,
        'Doctorate in Computer Science': 100,
        'Doctorate in Information Technology': 100,
        'Doctorate in Software Engineering': 100,
        'Master\'s Degree in Computer Science': 80,
        'Master\'s Degree in Information Technology': 80,
        'Master\'s Degree in Software Engineering': 80,
        'Bachelor\'s Degree in Computer Science': 60,
        'Bachelor\'s Degree in Information Technology': 60,
        'Bachelor\'s Degree in Software Engineering': 60,
    }
    degrees = education.get('degrees', [])
    if not degrees:
        return 40
    highest_score = max([degree_scores.get(degree.strip(), 0) for degree in degrees])
    return highest_score

def extract_experience(text):
    experience_years = 0

    current_year = datetime.datetime.now().year

    year_pattern = r'(\d+)\s+years'

    date_range_pattern = r'(\d{4})\s*-\s*(\d{4}|\bPresent\b)'

    total_years = 0
    detailed_experience = []

    year_matches = re.findall(year_pattern, text)
    for match in year_matches:
        years = int(match)
        total_years += years
        detailed_experience.append(f"{years} years of experience")

    date_matches = re.findall(date_range_pattern, text)
    for start_year, end_year in date_matches:
        start_year = int(start_year)
        if end_year.lower() == 'present':
            end_year = current_year
        else:
            end_year = int(end_year)
        
        years_in_range = end_year - start_year
        total_years += years_in_range
        detailed_experience.append(f"{years_in_range} years from {start_year} to {end_year}")

    return {'years': total_years, 'detailed_experience': detailed_experience}

def score_experience(experience):
    years = experience.get('years', 0)
    max_years = 10
    score = (years / max_years) * 100
    return min(score, 100)