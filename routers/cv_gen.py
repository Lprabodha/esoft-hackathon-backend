from jinja2 import Template
import pdfkit

# Extended sample data
cv_data = {
    "name": "John Doe",
    "title": "Full-Stack Software Engineer",
    "email": "john.doe@example.com",
    "phone": "+1-123-456-7890",
    "address": "123 Silicon Valley, California, USA",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe",
    "summary": "Passionate full-stack developer with 5+ years of experience building scalable web applications. Proficient in both frontend and backend technologies with a focus on delivering optimized, user-friendly solutions.",
    "skills": ["Python", "JavaScript", "React", "Node.js", "Django", "SQL", "MongoDB", "Docker", "Git", "CI/CD"],
    "experience": [
        {
            "role": "Senior Software Engineer",
            "company": "TechNova Inc.",
            "location": "San Francisco, CA",
            "years": "2021 - Present",
            "details": [
                "Designed and implemented a microservices architecture using Docker and Kubernetes.",
                "Built internal tools that reduced manual effort by 40% using Python and React.",
                "Led code reviews and mentored junior engineers."
            ]
        },
        {
            "role": "Software Developer",
            "company": "Innovatech Ltd.",
            "location": "Los Angeles, CA",
            "years": "2018 - 2021",
            "details": [
                "Developed e-commerce backend APIs using Django REST framework.",
                "Collaborated with UX designers to create responsive interfaces in React."
            ]
        }
    ],
    "education": [
        {
            "degree": "BSc in Computer Science",
            "institution": "University of California, Berkeley",
            "year": "2014 - 2018"
        }
    ],
    "projects": [
        {
            "name": "SmartInventory",
            "description": "An AI-powered inventory tracking system using Python and OpenCV to detect stock levels via camera feeds.",
            "link": "github.com/johndoe/smartinventory"
        },
        {
            "name": "Taskify",
            "description": "A lightweight task management web app built with React and Firebase for real-time sync.",
            "link": "taskify.web.app"
        }
    ],
    "certifications": [
        "AWS Certified Developer – Associate (2023)",
        "Certified Kubernetes Application Developer (2022)"
    ]
}

# Modern HTML Template
cv_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ name }} - CV</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; line-height: 1.6; color: #333; }
        h1, h2 { color: #2c3e50; margin-bottom: 5px; }
        h1 { font-size: 32px; }
        h2 { font-size: 20px; margin-top: 30px; }
        .title { font-size: 18px; color: #555; }
        .section { margin-bottom: 25px; }
        ul { margin: 0; padding-left: 20px; }
        .info { margin-top: -10px; font-size: 14px; color: #666; }
        .project-link { font-size: 13px; color: #0073b1; }
        .cert-item { margin-bottom: 5px; }
    </style>
</head>
<body>
    <h1>{{ name }}</h1>
    <div class="title">{{ title }}</div>
    <div class="info">
        {{ address }} | {{ phone }} | {{ email }}<br>
        <a href="https://{{ linkedin }}">{{ linkedin }}</a> | <a href="https://{{ github }}">{{ github }}</a>
    </div>

    <div class="section">
        <h2>Professional Summary</h2>
        <p>{{ summary }}</p>
    </div>

    <div class="section">
        <h2>Experience</h2>
        {% for job in experience %}
        <p><strong>{{ job.role }}</strong> - {{ job.company }} ({{ job.location }}, {{ job.years }})</p>
        <ul>
            {% for detail in job.details %}
            <li>{{ detail }}</li>
            {% endfor %}
        </ul>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Projects</h2>
        {% for project in projects %}
        <p><strong>{{ project.name }}</strong>: {{ project.description }}<br>
        <span class="project-link">{{ project.link }}</span></p>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Certifications</h2>
        {% for cert in certifications %}
        <div class="cert-item">- {{ cert }}</div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Education</h2>
        {% for edu in education %}
        <p><strong>{{ edu.degree }}</strong><br>{{ edu.institution }} ({{ edu.year }})</p>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Skills</h2>
        <p>{{ skills | join(', ') }}</p>
    </div>
</body>
</html>
"""

# Render the template
template = Template(cv_template)
html_cv = template.render(**cv_data)

# Save HTML file
with open("modern_cv.html", "w", encoding="utf-8") as f:
    f.write(html_cv)

# Path to wkhtmltopdf (adjust if installed elsewhere)
path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

# Convert to PDF
pdfkit.from_file("modern_cv.html", r"C:\Users\Kaleesha\Desktop\modern_cv_output1.pdf", configuration=config)
print("✅ Modern CV saved as 'modern_cv_output1.pdf'")
