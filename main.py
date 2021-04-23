import json
class Calendar:
    def __init__(self):
        self.lectures = []

class Lecture:
    def __init__(self, course_id, date, duration, lecure_hall, meeting_link):
        self.course_id = course_id
        self.date = date
        self.duration = duration
        self.lecure_hall = lecure_hall
        self.meeting_link = meeting_link

# Load 
def load_credentials():
    credentials = json.load("credentials.json")
    microsoft_token = credentials['microsoft-graph-token']
    afeka_token = credentials['afeka-token']

def compare_events(existing_events, target_calendar):

def update_target_calendar(calendar):
    account = Account(microsoft_token)
    afeka_calendar = account.getCalendar('Afeka')

def get_events