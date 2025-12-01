from constants import GRADE_THRESHOLDS, GRADE_NAMES
import math

class Grade():
    """ Repräsentiert eine einzelne LEK (Lern-Erfolgs_Kontrolle) mit Punkten und Noten."""
    def __init__(self, max_points, achieved_points):

        self.max_points = max_points
        self.achieved_points = achieved_points
        self.percentage = 0
        self.grade = 0

        self.calculate_percentage()
        self.calculate_grade()

    def calculate_percentage(self):
        """Berechnet den Prozentsatz aus erreichten und maximalen Punkten"""
        if self.max_points == 0:
            self.percentage = 0
            return
        
        self.percentage = round((self.achieved_points / self.max_points) * 100, 2)

    def calculate_grade(self):
        """Berechnet die Note anhand der erreichten Prozentzahl"""
        for note in [1, 2, 3, 4, 5, 6]:
            if self.percentage >= GRADE_THRESHOLDS[note]:
                self.grade = note
                return
    
    def get_grade_name(self):
        """Ermittelt den Namen der Note (z.B. 1= 'sehr gut', 2='gut' u.s.w."""
        return GRADE_NAMES[self.grade]
    
    def to_dict(self):
        return {"max_points": self.max_points, "achieved_points": self.achieved_points, "percentage": self.percentage, "grade": self.grade}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["max_points"], data["achieved_points"])
    
    @staticmethod
    def calculate_required_points(target_grade, max_points):
        required = (GRADE_THRESHOLDS[target_grade] / 100) * max_points
        return math.ceil(required)
