import os
import json
from subject import Subject

def save_subjects(subjects, filename):

    try:
        data = [s.to_dict() for s in subjects]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        return False


def load_subjects(filename):
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return [Subject.from_dict(d) for d in data]
        
    except (json.JSONDecodeError, KeyError, Exception):
        return[]