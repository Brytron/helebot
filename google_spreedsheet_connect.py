from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def initial_drive():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token_drive.pickle'):
        with open('token_drive.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_drive.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token_drive.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)



def excel_to_sheets(service,excel_file):

    mime_type = "application/vnd.ms-excel"
    meta = {'name':excel_file, 'mimeType':"application/vnd.google-apps.spreadsheet"}
    media = MediaFileUpload(filename=excel_file, mimetype=mime_type)

    file = service.files().create(body=meta,
                                        media_body=media,
                                        fields='webViewLink, id',).execute()

    file_id = file.get('id')
    permit_metadata = {'role': 'writer', 'type': 'anyone'}
    permit = service.permissions().create(fileId=file_id, body=permit_metadata).execute()
    print(permit)
    return file.get('webViewLink')


#service = initial_drive()
#print(excel_to_sheets(service,"glory_base.xlsx"))

