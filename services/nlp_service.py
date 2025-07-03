import spacy
from typing import List, Dict

# Load a pre-trained spaCy model
# Make sure you've run: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
    # Fallback to a blank model or raise an error depending on desired behavior
    nlp = spacy.blank("en") # Fallback for demo purposes

# --- Dummy Skill Ontology (In a real app, this would be from DB or a more complex file) ---
# This is a simplified list for demonstration.
# In practice, you'd fetch this from your `skills` table.
SKILL_ONTOLOGY = {
    "python": {"category": "Programming", "related": ["django", "flask", "data analysis"]},
    "java": {"category": "Programming", "related": []},
    "javascript": {"category": "Programming", "related": ["react", "nodejs", "typescript"]},
    "data analysis": {"category": "Data Science", "related": ["sql", "excel", "pandas", "r"]},
    "machine learning": {"category": "AI/ML", "related": ["deep learning", "tensorflow", "pytorch"]},
    "project management": {"category": "Soft Skills", "related": ["agile", "scrum"]},
    "sql": {"category": "Database", "related": ["mysql", "postgresql"]},
    "react": {"category": "Frontend", "related": ["javascript", "frontend development"]},
    "nodejs": {"category": "Backend", "related": ["javascript", "backend development"]},
    "cloud computing": {"category": "DevOps", "related": ["aws", "azure", "gcp"]},
    "communication": {"category": "Soft Skills", "related": []},
    "teamwork": {"category": "Soft Skills", "related": []},
    "problem solving": {"category": "Soft Skills", "related": []},
    "excel": {"category": "Data Analysis", "related": []},
    "r": {"category": "Data Analysis", "related": []},
    "django": {"category": "Backend", "related": ["python"]},
    "flask": {"category": "Backend", "related": ["python"]},
    "typescript": {"category": "Programming", "related": ["javascript"]},
    "frontend development": {"category": "Web Development", "related": ["html", "css", "javascript", "react"]},
    "backend development": {"category": "Web Development", "related": ["python", "nodejs", "java"]},
}

def extract_skills_from_text(text: str) -> List[Dict[str, str]]:
    """
    Extracts skills from a given text using spaCy and a simple keyword matching approach.
    In a real application, this would be more sophisticated (e.g., custom NER, semantic similarity).
    """
    doc = nlp(text.lower()) # Process text in lowercase

    found_skills = set()
    # Simple keyword matching against our ontology for hackathon
    for skill_name in SKILL_ONTOLOGY.keys():
        if skill_name in doc.text:
            found_skills.add(skill_name)

    # You could also use spaCy's PhraseMatcher for more robust keyword matching
    # from spacy.matcher import PhraseMatcher
    # matcher = PhraseMatcher(nlp.vocab)
    # patterns = [nlp.make_doc(skill_name) for skill_name in SKILL_ONTOLOGY.keys()]
    # matcher.add("SKILL_PATTERNS", patterns)
    # matches = matcher(doc)
    # for match_id, start, end in matches:
    #     span = doc[start:end]
    #     found_skills.add(span.text)

    # Convert found skills to a list of dictionaries for consistent output
    return [{"name": skill} for skill in sorted(list(found_skills))]

# Example usage:
if __name__ == "__main__":
    sample_text = "I am proficient in Python and have experience with data analysis using pandas. I also know a bit of React for frontend development."
    extracted = extract_skills_from_text(sample_text)
    print(f"Extracted skills: {extracted}")

    sample_text_2 = "My project involved machine learning with TensorFlow and deep learning concepts. I also managed the project using agile methodologies."
    extracted_2 = extract_skills_from_text(sample_text_2)
    print(f"Extracted skills 2: {extracted_2}")