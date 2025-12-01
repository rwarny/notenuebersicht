from grade import Grade

class Subject():
    """Repräsentiert ein Fach mit mehreren LEKs und berechnet Durchschnitte"""
    def __init__(self, name):
        self.name = name
        self.grades = []
        self.average = None

    def add_grade(self, grade):
        self.grades.append(grade)
        self.calculate_average()

    def remove_grade(self, index):
        self.grades.pop(index)
        self.calculate_average()

    def calculate_average(self):
        """Berechnet den Durchschnitt"""
        if len(self.grades) == 0:
            self.average = None
            return
        
        summe = sum([g.grade for g in self.grades])
        self.average = round(summe / len(self.grades), 2)

    def get_best_grade(self):
        return min([g.grade for g in self.grades])
    
    def get_worst_grade(self):
        return max([g.grade for g in self.grades])
    
    def get_grade_history(self):
        return [g.grade for g in self.grades]
    
    def to_dict(self):
        return {"name": self.name, "grades": [g.to_dict() for g in self.grades]}

    @classmethod
    def from_dict(cls, data):
        subject = cls(data["name"])
        for grade_data in data["grades"]:
            grade = Grade.from_dict(grade_data)
            subject.add_grade(grade)
        return subject
    
    def calculate_needed_grade_for_average(self, target_average):
        """Berechnet die benötigte Note für einen gewünschten Durchschnitt"""
        aktuelle_summe = sum([g.grade for g in self.grades])
        n = len(self.grades)
        needed = round((target_average * (n+1) - aktuelle_summe), 2)

        if needed < 1:
            return None  # Ziel nicht mehr erreichbar (zu gut)
        if needed > 6:
            return None  # Ziel nicht erreichbar (zu schlecht)
        
        return needed
    