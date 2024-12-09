ResuMatch: Intelligent Candidate and Company Qualification Matcher

Version: 1.0
Author: [Group 4 Resumatch]

Overview
ResuMatch is a Python-based resume evaluation system that automates the extraction, analysis, and scoring of resumes. The system leverages NLP (Natural Language Processing) techniques, 
regex-based pattern matching, and fuzzy matching algorithms to assess the qualification, skills, education, and experience of job applicants.

Key Features
Text Extraction

Supports both PDF (.pdf) and Word (.docx) formats.
Ensures accurate text extraction and handles errors gracefully.
Information Extraction

Applicant Details: Extracts name, email, and phone number using NLP and regex.
Skills: Detects both predefined and similar skills using regex and fuzzy matching.
Education: Identifies degrees and institutions using regex and spaCy NER.
Experience: Parses years of experience and date ranges to calculate total experience.
Resume Scoring

Skills Score: Evaluates the presence of predefined skills.
Education Score: Scores degrees based on relevance to the field.
Experience Score: Scores total years of professional experience.
Qualification Grade: Combines all scores into a weighted average.
Customizable

Skill sets, degree patterns, and scoring logic can be modified to suit specific job roles.
Accurate and Readable Outputs

Scores are rounded to two decimal places for clarity and precision.
Outputs detailed feedback, including detected skills, education, and experience breakdown.
System Requirements
Python Version: 3.7+


Dependencies:

spacy (with en_core_web_sm model)
PyPDF2
docx2txt
fuzzywuzzy
collections (standard library)
Install dependencies with:

bash
Copy code
pip install spacy PyPDF2 python-docx fuzzywuzzy
python -m spacy download en_core_web_sm


Provide a file path to a resume (PDF or DOCX).
Processing:

Extracts text from the resume.

Analyzes the text to extract relevant applicant details, skills, education, and experience.
Scores and grades the resume based on predefined criteria.

Returns a summary of applicant details.

Provides scores for skills, education, experience, and an overall qualification grade.

resume_path = "path/to/resume.pdf"  # Replace with the resume file path
applicant_info, qualification_grade, skills_score, education_score, experience_score = evaluate_resume(resume_path)

# Output results

print("Applicant Info:", applicant_info)

print("Qualification Grade:", qualification_grade)

print("Skills Score:", skills_score)

print("Education Score:", education_score)

print("Experience Score:", experience_score)


Limitations

Assumes resumes are in English.
Limited handling of non-standard resume formats or unconventional layouts.
Requires additional configuration for specific job roles or industries.

Future Enhancements

Add support for JSON and CSV outputs.
Implement cloud-based resume processing for scalability.
Incorporate job description matching for targeted evaluations.
Expand support for non-English resumes using multilingual NLP models.
