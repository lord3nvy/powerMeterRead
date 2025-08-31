import imaplib
import email
import os

# Email credentials and settings
EMAIL = 'etl.ing244819f@yahoo.com'
PASSWORD = 'N,M2\\SIn.l5Ju"IqvCem'
IMAP_SERVER = 'imap.mail.yahoo.com'  # Change if using Outlook, Yahoo, etc.
SENDER = 'sender@example.com'
#SAVE_DIR = 'C:/path/to/save/attachments'

print(PASSWORD)

# Connect to the server
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('inbox')

# Search for emails from the specified sender
status, data = mail.search(None, f'FROM "{SENDER}"')

# Process each email
# for num in data[0].split():
#     status, msg_data = mail.fetch(num, '(RFC822)')
#     raw_email = msg_data[0][1]
#     msg = email.message_from_bytes(raw_email)

#     for part in msg.walk():
#         if part.get_content_maintype() == 'multipart':
#             continue
#         if part.get('Content-Disposition') is None:
#             continue

#         filename = part.get_filename()
#         if filename:
#             filepath = os.path.join(SAVE_DIR, filename)
#             with open(filepath, 'wb') as f:
#                 f.write(part.get_payload(decode=True))
#             print(f'Saved: {filepath}')

mail.logout()
