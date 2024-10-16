from enum import Enum

class Major(Enum):
    AERONAUTICAL_ENGINEERING = ("Aeronautical Engineering", "Aero")
    APPLIED_PHYSICS = ("Applied Physics", "ApPhys")
    ARCHITECTURE = ("Architecture", "Archi")
    BIOLOGY = ("Biology", "Bio")
    BIOMEDICAL_ENGINEERING = ("Biomedical Engineering", "BME")
    BUSINESS_ANALYTICS = ("Business Analytics", "BA")
    BUSINESS_AND_MANAGEMENT = ("Business and Management", "BMGT")
    CHEMICAL_ENGINEERING = ("Chemical Engineering", "ChemE")
    CHEMISTRY = ("Chemistry", "Chem")
    CIVIL_ENGINEERING = ("Civil Engineering", "CivE")
    COGNITIVE_SCIENCE = ("Cognitive Science", "CogSci")
    COMPUTER_AND_SYSTEMS_ENGINEERING = ("Computer and Systems Engineering", "CSE")
    COMPUTER_SCIENCE = ("Computer Science", "CS")
    ECONOMICS = ("Economics", "Econ")
    ELECTRICAL_ENGINEERING = ("Electrical Engineering", "EE")
    ENVIRONMENTAL_ENGINEERING = ("Environmental Engineering", "EnvE")
    ENVIRONMENTAL_SCIENCE = ("Environmental Science", "EnvS")
    GAMES_AND_SIMULATION_ARTS_AND_SCIENCES = ("Games and Simulation Arts and Sciences", "GSAS")
    GEOLOGY = ("Geology", "Geo")
    INDUSTRIAL_AND_MANAGEMENT_ENGINEERING = ("Industrial and Management Engineering", "IME")
    INFORMATION_TECHNOLOGY_AND_WEB_SCIENCE = ("Information Technology and Web Science", "ITWS")
    MATERIALS_ENGINEERING = ("Materials Engineering", "MatSci")
    MATHEMATICS = ("Mathematics", "Math")
    MECHANICAL_ENGINEERING = ("Mechanical Engineering", "MechE")
    MUSIC = ("Music", "Music")
    NUCLEAR_ENGINEERING = ("Nuclear Engineering", "NucE")
    PHILOSOPHY = ("Philosophy", "Phil")
    PHYSICS = ("Physics", "Phys")
    PSYCHOLOGICAL_SCIENCE = ("Psychological Science", "PsychS")
    SCIENCE_TECHNOLOGY_AND_SOCIETY = ("Science, Technology, and Society", "STS")
    SUSTAINABILITY_STUDIES = ("Sustainability Studies", "SustS")

    def __init__(self, major: str, alias: str):
        self.major = major
        self.alias = alias

