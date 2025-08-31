import imaplib
import email
import os

class EmailAttachmentDownloader:
    def __init__(self, email_address, password, imap_server, sender, save_dir):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.sender = sender
        self.save_dir = save_dir
        self.mail = None

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(self.email_address, self.password)
        self.mail.select('inbox')

    def download_attachments(self):
        status, data = self.mail.search(None, f'FROM "{self.sender}"')
        for num in data[0].split():
            status, msg_data = self.mail.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if filename:
                    filepath = os.path.join(self.save_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    print(f'Saved: {filepath}')

    def logout(self):
        if self.mail:
            self.mail.logout()


