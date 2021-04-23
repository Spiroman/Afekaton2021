from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json
import sys

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
calendar_id = ''

class Calendar:
    def __init__(self):
        self.events = dict()

    def add_event(self, event):
        self.events[event.id] = event.event

class Event:
    def __init__(self, event):
        self.event = event
        class_id = event['summary'].split('*')
        if len(class_id) == 1:
            class_id = class_id[0]
        else:
            class_id = class_id[1]

        self.id = '%s_%s_%s_%s_%s' % (
            class_id[0:5],
            event['description'][7:10],
            event['description'].split('Lecturer: ')[0] if len(event['description'].split('Lecturer: ')) == 1 else event['description'].split('Lecturer: ')[1],
            event['start']['dateTime'],
            event['end']['dateTime']
        )         

def get_calendar_id():
    with open('store.json') as store:
        data = json.load(store)
        return data['calendar_id']

def load_calendar(file_name):
    calendar = Calendar()
    # Opening JSON file
    with open(file_name) as json_file:
        data = json.load(json_file)
        for json_event in data['events']:
            event = Event(json_event)
            calendar.add_event(event)
    return calendar

def create_google_calendar(service, calendarName = 'Afeka'):
    calendar = {
        'summary': calendarName,
        'timeZone': 'Asia/Jerusalem'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    id = created_calendar['id']
    with open('store.json', 'r+') as store:
        data = {'calendar_id': str(id)}        
        store.seek(0)
        json.dump(data, store)
        store.truncate()
    return id

def delete_google_calendar(service, calendar_id):
    service.calendars().delete(calendarId=calendar_id).execute()

def populate_google_calendar(service, calendar_id, calendar):
    for (key, event) in calendar.events.items():
        service.events().insert(calendarId = calendar_id, body=event).execute()

def recreate(service, calendar):
    calendar_id = get_calendar_id()
    delete_google_calendar(service, calendar_id)
    new_id = create_google_calendar(service)
    populate_google_calendar(service, new_id, calendar)

def compare_calendars(service):
    old_calendar = load_calendar('old_classes.json')
    new_calendar = load_calendar('new_classes.json')
    old_events_ids = list(old_calendar.events.keys())
    new_events_ids = list(new_calendar.events.keys())
    old_events_ids.sort()
    new_events_ids.sort()
    if len(old_events_ids) != len(new_events_ids):
        recreate(new_calendar)
    else:
        for i in range(len(new_events_ids)):
            if old_events_ids[i] != new_events_ids[i]:
                recreate(service, new_calendar)

def get_calendar_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def load_inital_calendar(service):
    calendar_id = str(get_calendar_id())
    with open('old_classes.json') as json_file:
        data = json.load(json_file)
        for event in data['events']:
            google_event = service.events().insert(calendarId = calendar_id, body = event).execute()
            

def initial_flow(service):
    create_google_calendar(service)
    load_inital_calendar(service)

def second_flow(service):
    compare_calendars(service)

def main():
    service = get_calendar_service()
    if sys.argv[1] == 'init':
        initial_flow(service)
    else:
        second_flow(service)

if __name__ == '__main__':
    main()