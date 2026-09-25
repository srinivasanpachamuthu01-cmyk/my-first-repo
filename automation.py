import os
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define required Google API Scopes for Gmail and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

SPREADSHEET_ID = '1EuDqvZ8v_kJ3e9EiNH699z-3U0DLMM1KzqcJ263gihc'

def authenticate():
    """Authenticates the user and returns initialized Gmail and Sheets services."""
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                if os.path.exists('token.json'):
                    os.remove('token.json')
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found in 'D:\\python files\\credentials.json'"
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    gmail_service = build('gmail', 'v1', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    return gmail_service, sheets_service

def append_to_sheet(sheets_service, sender, subject, snippet):
    """Appends an email record as a new row in Google Sheets."""
    values = [[sender, subject, snippet]]
    body = {'values': values}
    
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A:C",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def main():
    print("Initializing Google Services...")
    gmail_service, sheets_service = authenticate()
    
    # Store today's date formatted for Gmail search query (YYYY/MM/DD)
    start_date = datetime.now().strftime('%Y/%m/%d')
    # Keep track of already logged email IDs so nothing repeats
    processed_ids = set()

    print(f"Workflow started! Listening for real-time incoming emails received after {start_date}...\n")

    while True:
        try:
            # Query ONLY unread emails received from today onwards
            query = f'is:unread label:INBOX after:{start_date}'
            results = gmail_service.users().messages().list(
                userId='me', q=query
            ).execute()
            
            messages = results.get('messages', [])

            # Filter out messages we have already logged in this run session
            new_messages = [m for m in messages if m['id'] not in processed_ids]

            if new_messages:
                print(f"New incoming email detected! Processing {len(new_messages)} message(s)...")
                
                for msg in new_messages:
                    msg_detail = gmail_service.users().messages().get(
                        userId='me', id=msg['id']
                    ).execute()
                    
                    # Parse Headers (Sender & Subject)
                    headers = msg_detail.get('payload', {}).get('headers', [])
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    snippet = msg_detail.get('snippet', '')

                    # Append to Google Sheet
                    append_to_sheet(sheets_service, sender, subject, snippet)
                    print(f" -> Appended to sheet: '{subject}' from {sender}")

                    # Mark as processed in local memory and mark as READ in Gmail
                    processed_ids.add(msg['id'])
                    gmail_service.users().messages().batchModify(
                        userId='me',
                        body={
                            'ids': [msg['id']],
                            'removeLabelIds': ['UNREAD']
                        }
                    ).execute()
            else:
                print("Waiting for new messages... (checking every 15 seconds)")

        except HttpError as error:
            print(f"Google API Error occurred: {error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Check every 15 seconds for fast real-time response
        time.sleep(15)

if __name__ == '__main__':
    main()
