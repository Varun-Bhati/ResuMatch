from backend.services.resume_scoring_service import calculate_resume_score
from backend.services.text_preprocessor import clean_text
from backend.services.section_detector import detect_sections
from backend.services.esco_service import extract_esco_skills
from backend.services.onet_service import extract_onet_software
from backend.services.concept_service import merge_concepts


TEST_RESUMES = {

    "1. Extremely Short": """
    John Doe
    Skills
    Python
    """,

    "2. Short Student Resume": """
    JOHN DOE
    B.Tech Computer Science Student

    Education
    B.Tech in Computer Science and Engineering — Expected 2029

    Skills
    Python, SQL, Machine Learning, Git

    Projects
    Resume Analyzer — Built a Flask application for resume analysis.

    Experience
    Student Developer — Practicing Python and web development.
    """,

    "3. Good Student Resume": """
    JOHN DOE
    B.Tech Computer Science Student
    john.doe@email.com
    +91 9876543210
    linkedin.com/in/johndoe
    github.com/johndoe

    Summary
    Computer Science student interested in software development and
    artificial intelligence. Experienced in building Python-based
    applications and working with machine learning concepts.

    Education
    B.Tech in Computer Science and Engineering — Expected 2029
    Relevant coursework includes Data Structures, Database Systems,
    Operating Systems, and Machine Learning.

    Skills
    Python, SQL, Data Structures, Machine Learning, Git, Flask,
    Pandas, NumPy

    Projects
    Resume Analyzer
    Built a Flask-based application that extracts resume information,
    identifies technical concepts, evaluates resume structure, and
    provides improvement suggestions.

    Student Management System
    Developed a Python and SQL application for managing student records,
    including database operations and basic search functionality.

    Experience
    Student Developer
    Practiced Python programming, web development, database management,
    and machine learning fundamentals through academic projects.
    """,

    "4. Strong Professional Resume": """
    JANE DOE
    Software Engineer
    jane.doe@email.com
    +91 9876543210
    linkedin.com/in/janedoe
    github.com/janedoe

    Summary
    Software Engineer with experience developing scalable web applications,
    data processing pipelines, and machine learning solutions. Experienced
    in Python, SQL, Flask, cloud technologies, and software development.

    Education
    B.Tech in Computer Science and Engineering
    ABC University — 2021

    Skills
    Python, SQL, Java, Machine Learning, Flask, Django, Git,
    Docker, Kubernetes, AWS, PostgreSQL, Pandas, NumPy

    Experience
    Software Engineer
    ABC Technologies — 2023 to Present
    Developed and maintained Python web applications used by internal teams.
    Designed REST APIs and database integrations.
    Improved application performance through query optimization.
    Built automated data processing workflows and testing pipelines.
    Collaborated with developers and product teams to deliver production
    features.

    Software Engineering Intern
    XYZ Labs — 2022 to 2023
    Developed backend services using Python and Flask.
    Created SQL queries for reporting and data analysis.
    Implemented automated tests and participated in code reviews.

    Projects
    Machine Learning Platform
    Built a machine learning pipeline for data preprocessing, model
    training, evaluation, and deployment.
    Developed reusable Python components and documented the workflow.

    Certifications
    AWS Certified Cloud Practitioner
    """,

    "5. Very Long Resume": """
JOHN DOE
Senior Software Engineer
john.doe@email.com
+91 9876543210
linkedin.com/in/johndoe
github.com/johndoe

Summary
Experienced software engineer with a strong background in software development,
distributed systems, databases, cloud computing, artificial intelligence,
machine learning, data engineering, application development, testing,
deployment, architecture, monitoring, technical documentation, system design,
software quality, and technical leadership. Experienced in designing and
implementing reliable software systems for different business requirements.

Education
Master of Technology in Computer Science
University of Technology — 2022

Bachelor of Technology in Computer Science and Engineering
University of Technology — 2020

Relevant coursework includes Data Structures, Algorithms, Database Management,
Operating Systems, Computer Networks, Software Engineering, Artificial
Intelligence, Machine Learning, Distributed Systems, Cloud Computing, and
Information Security.

Skills
Python, Java, C++, JavaScript, TypeScript, SQL, PostgreSQL, MySQL, MongoDB,
Redis, Flask, Django, FastAPI, React, Node.js, Git, Docker, Kubernetes, AWS,
Azure, Linux, Machine Learning, Deep Learning, Natural Language Processing,
Data Engineering, Apache Spark, Apache Kafka, Airflow, Pandas, NumPy,
TensorFlow, PyTorch, REST APIs, Microservices, CI/CD, Testing, System Design,
Database Design, Data Processing, Cloud Architecture, Agile Development.

Experience
Senior Software Engineer
ABC Technologies — 2023 to Present

Led the development and maintenance of multiple software systems used by
engineering, operations, and business teams. Designed backend services and
REST APIs using Python, Flask, and FastAPI. Worked with relational and
NoSQL databases and designed database schemas for different application
requirements.

Implemented application features, authentication systems, authorization
controls, database integrations, background processing, logging, monitoring,
and automated testing. Improved application performance by identifying
slow database queries and optimizing application workflows.

Designed distributed data processing workflows for large datasets. Worked
with Python, Apache Spark, Apache Kafka, and cloud infrastructure to process
and transform application data. Created monitoring processes to identify
failures and performance issues.

Collaborated with software engineers, product managers, designers, testers,
security teams, and infrastructure engineers. Participated in architecture
discussions, technical planning, code reviews, debugging sessions, and
production support activities.

Developed reusable software components and internal libraries to reduce
repeated implementation work across projects. Maintained technical
documentation describing system architecture, APIs, configuration,
deployment procedures, and troubleshooting steps.

Software Engineer
XYZ Corporation — 2021 to 2023

Developed backend services and internal applications using Python and Java.
Created REST APIs and integrated applications with relational databases.
Designed SQL queries for reporting, data analysis, and application
operations.

Built data processing workflows using Python and Apache Spark. Developed
data validation checks and automated processing tasks. Worked with Git for
source control and participated in collaborative software development
workflows.

Created automated unit and integration tests for backend services.
Investigated application defects, reproduced reported issues, identified
root causes, and implemented fixes. Participated in code reviews and
provided feedback on maintainability and software quality.

Worked with Docker to containerize applications and supported deployment
workflows in cloud environments. Assisted with monitoring, logging,
configuration management, and troubleshooting of deployed applications.

Software Engineering Intern
XYZ Labs — 2020 to 2021

Developed small backend features using Python and Flask. Created SQL
queries for data retrieval and reporting. Assisted senior engineers with
testing, debugging, documentation, and application maintenance.

Worked with Git and followed team development practices including branches,
commits, pull requests, and code reviews. Built small scripts to automate
repetitive development and data processing tasks.

Projects
Enterprise Data Platform

Designed and implemented a scalable data processing platform for collecting,
transforming, validating, and storing data from multiple sources. Integrated
Apache Kafka for event streaming and Apache Spark for distributed processing.

Created data validation procedures to identify incomplete, duplicate, or
incorrect records before downstream processing. Implemented monitoring
mechanisms and logging to help identify pipeline failures.

Designed database structures for processed datasets and created documentation
for developers working with the platform. Worked with Python to implement
data processing components and automation scripts.

Machine Learning Platform

Developed a machine learning pipeline supporting data preprocessing,
feature engineering, model training, evaluation, and deployment.

Implemented Python components for preparing datasets and evaluating model
performance. Used Pandas and NumPy for data manipulation and numerical
operations. Experimented with machine learning algorithms and compared
their performance using appropriate evaluation metrics.

Created documentation describing the workflow from raw data collection to
model evaluation. Structured the project so individual processing steps
could be tested and reused.

Resume Analysis Application

Built a Flask-based web application capable of extracting information from
resume documents and analyzing their structure and technical content.

Implemented document processing, text cleaning, section detection, technical
concept extraction, resume scoring, ATS analysis, and job matching features.
Integrated standardized datasets to identify skills, knowledge areas, and
software technologies.

Designed backend services for resume analysis and created API endpoints
for communicating with the frontend application. Added validation and
error handling for unsupported documents and incomplete input.

Web Application

Developed a full-stack web application using React, Flask, PostgreSQL,
Docker, and AWS. Implemented user authentication, authorization, API
integration, database operations, logging, testing, and deployment workflows.

Designed backend endpoints for creating, updating, retrieving, and deleting
application data. Created frontend components for displaying information
returned by backend services.

Data Analytics Dashboard

Created a dashboard for analyzing operational data and presenting useful
metrics to users. Used Python and Pandas for data preparation and
transformation.

Implemented filtering and aggregation operations and created reports for
different categories of data. Added validation checks to reduce errors
during data processing.

Cloud Deployment Project

Configured a cloud-based environment for deploying a Python web application.
Used Docker to package application dependencies and created deployment
configuration for the application.

Implemented logging and monitoring procedures to identify application
errors and resource problems. Documented the deployment process so the
application could be reproduced in another environment.

Certifications
AWS Certified Solutions Architect
Microsoft Azure Fundamentals
Kubernetes Application Developer
Python Programming Certification
Database Management Certification

Additional Information
Open-source contributor, technical writer, mentor, conference speaker,
community organizer, coding workshop volunteer, and participant in
software development communities.

Professional Activities
Regularly participate in technical discussions and software development
communities. Follow developments in artificial intelligence, machine
learning, cloud computing, software engineering, distributed systems,
data engineering, and developer tools.

Contribute to small open-source projects and maintain personal programming
projects to improve practical development skills. Practice writing
technical documentation and explaining programming concepts through
educational content.

Technical Interests
Artificial intelligence, machine learning, natural language processing,
large language models, data engineering, cloud computing, distributed
systems, backend development, software architecture, databases,
information retrieval, developer tools, and applied software engineering.

Career Development
Continue developing software engineering skills through practical projects,
technical study, experimentation, and collaborative development. Interested
in building reliable software systems and applying machine learning and
data processing techniques to practical problems.

Professional Development
Complete technical courses, participate in programming exercises, review
software engineering practices, study system design concepts, and build
projects using modern development technologies. Maintain a learning routine
focused on improving programming, databases, cloud technologies, machine
learning, and software development knowledge.

Project Documentation
Maintain documentation for personal and professional projects including
architecture notes, implementation details, API descriptions, configuration
instructions, testing procedures, and deployment steps. Documentation is
updated when major implementation changes are introduced.

Software Development Practices
Follow version control practices using Git. Use structured development
workflows, testing, debugging, code review, documentation, and incremental
implementation when developing software applications.

Data Practices
Work with structured and semi-structured data using Python and SQL.
Perform data cleaning, transformation, validation, aggregation, and
analysis before using datasets in applications or machine learning
experiments.

Engineering Collaboration
Work collaboratively with developers and technical teams. Participate in
planning discussions, code reviews, debugging sessions, documentation,
testing activities, and technical problem solving.

Continuous Learning
Regularly practice programming and software development concepts through
hands-on projects and technical exercises. Explore new frameworks, tools,
libraries, and development practices when they are relevant to current
projects and learning goals.
"""
}


def analyze_test_resume(name, text):

    cleaned_text = clean_text(text)

    sections = detect_sections(cleaned_text)

    esco_matches = extract_esco_skills(cleaned_text)

    skills = [
        match
        for match in esco_matches
        if match["skill_type"] == "skill/competence"
    ]

    knowledge = [
        match
        for match in esco_matches
        if match["skill_type"] == "knowledge"
    ]

    onet_software = extract_onet_software(cleaned_text)

    technical_concepts = merge_concepts(
        esco_matches,
        onet_software
    )

    word_count = len(cleaned_text.split())

    result = calculate_resume_score(
        cleaned_text,
        word_count,
        sections,
        skills,
        knowledge,
        technical_concepts
    )

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    print(f"Word count: {word_count}")
    print(f"Resume score: {result['total_score']}/100")

    print()
    print("Score breakdown:")

    for item in result["breakdown"]:
        print(
            f"  {item['category']}: "
            f"{item['score']}/{item['max_score']}"
        )

    print()
    print("Technical concepts:")
    print(f"  ESCO skills: {len(skills)}")
    print(f"  ESCO knowledge: {len(knowledge)}")
    print(f"  O*NET technologies: {len(onet_software)}")
    print(f"  Unified concepts: {len(technical_concepts)}")

    print()
    print("Sections:")

    for section, detected in sections.items():
        print(
            f"  {section}: "
            f"{'Yes' if detected else 'No'}"
        )

    print()
    print("Readability signals:")

    for signal, value in result["signals"]["readability"].items():
        print(
            f"  {signal}: {value}"
        )


for name, resume_text in TEST_RESUMES.items():
    analyze_test_resume(
        name,
        resume_text
    )

print()
print("=" * 70)
print("SCORING DIAGNOSTIC COMPLETE")
print("=" * 70)