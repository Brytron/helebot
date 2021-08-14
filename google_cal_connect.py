from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import dateutil.parser as parser
import pytz

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
cal_id = 'dc2nffnn767bbkujgkn008usoo@group.calendar.google.com'


class SimpleEvent:
    """return minimum results for events"""
    def __init__(self):
        self.summary = None
        self.time = None
        self.eventId = None


def initial_cal():
    """initializes calandar tokens
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_events():

    service = initial_cal()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId = cal_id, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def next_event(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId = cal_id, timeMin=now,
                                        maxResults=1, singleEvents=True,
                                        orderBy='startTime').execute()
    try:
        out = events_result.get('items', [0])[0]
    except IndexError:
        out = None

    return out




def get_weeks_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    max = datetime.datetime.utcnow() + datetime.timedelta(weeks = 1)
    max_iso = max.isoformat() + 'Z'
    events_result = service.events().list(calendarId = cal_id, timeMin=now, timeMax=max_iso,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    return events_result.get('items', [])


def delete_event(service,event_name):
    if event_name == "next":
        event_id = next_event(service)['id']
    else:
        event_id = find_full_event(service, event_name)['id']
    service.events().delete(calendarId=cal_id, eventId=event_id).execute()


def show_cal_list():
    service = initial_cal()
    cal_list = service.calendarList().list().execute()
    cals = cal_list.get('items', [])
    print(cals)


def find_full_event(service, query):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming events')
    events_result = service.events().list(calendarId='dc2nffnn767bbkujgkn008usoo@group.calendar.google.com',
                                        timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('no events not found.')
    else:
        for event in events:
            if event['summary'] == query:
                return event
    return None


def find_event(service, query):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming events')
    events_result = service.events().list(calendarId='dc2nffnn767bbkujgkn008usoo@group.calendar.google.com',
                                        timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('no events not found.')
    for event in events:
        if event['summary'] == query:
            result = SimpleEvent()
            result.time = event['start'].get('dateTime', event['start'].get('date'))
            result.summary = event['summary']
            return result
    return None


def create_event(service, event_name, month: str, day: str, start_time='12:00am', end_time = "11:59pm", timezone='PST'):
    service.events().quickAdd(calendarId=cal_id,text=f"{event_name} on {month} {day} {start_time}-{end_time}").execute()


def time_to(time_event, timezone_str ='US/Pacific'):
    timezone = pytz.timezone(timezone_str)
    date_1 = parser.parse(time_event)
    #print(date_1)
    date_2 = datetime.datetime.now(timezone)
    #print(date_2)
    return date_1 - date_2


def show_cal(service):
    return service.calendarList().get(calendarId='dc2nffnn767bbkujgkn008usoo@group.calendar.google.com').execute()


def pretty_event(event):
    name = event['summary']
    start = parser.parse(event['start'].get('dateTime'))
    return start.strftime(f'{name} starts on %a %d at %I:%M %p')


def pretty_week():
    today = datetime.datetime.now()
    return today.strftime("Upcoming events for the week of %x")


def main():
    print(pretty_week())

#main()

