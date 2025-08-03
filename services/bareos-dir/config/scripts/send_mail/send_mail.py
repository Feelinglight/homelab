from email.utils import parseaddr
import re
import argparse
import smtplib
from email.mime.text import MIMEText


def send_mail(smtp_address: str, smtp_port, smtp_login: str, smtp_password: str, from_: str,
              recipients: list[str], subject: str, email_text: str):
    with smtplib.SMTP(smtp_address, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_login, smtp_password)
        server.set_debuglevel(1)
        _, from_email = parseaddr(from_)

        text = MIMEText(email_text, 'html')
        text['From'] = from_
        text['Subject'] = subject

        for recipient in recipients:
            text['To'] = recipient
            server.sendmail(from_email, recipient, text.as_string())


def not_empty_string(arg_name):
    def validate(string):
        if not string:
            raise argparse.ArgumentTypeError(f'Argument "{arg_name}" cannot be empty')
        return string
    return validate


def email_type(arg_name):
    def validate_email(email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise argparse.ArgumentTypeError(
                f'Argument "{arg_name}": invalid email address: "{email}"')
        return email
    return validate_email


def email_from_type(arg_name):
    def validate_email_from(from_):
        try:
            from_, email = parseaddr(from_)
            email_type(arg_name)(email)
        except IndexError:
            raise argparse.ArgumentTypeError(
                f'Argument "{arg_name}": wrong format. Must be "From <Email>"')
        return validate_email_from


def main():
    parser = argparse.ArgumentParser(description='Send email via SMTP')

    parser.add_argument('--smtp-address', type=not_empty_string("smtp-address"),
                        help='SMTP server address', required=True)
    parser.add_argument('--smtp-port', type=int,
                        help='SMTP server port', required=True)
    parser.add_argument('--smtp-login', type=not_empty_string("smtp-login"),
                        help='SMTP login', required=True)
    parser.add_argument('--smtp-password', type=not_empty_string("smtp-password"),
                        help='SMTP password', required=True)
    parser.add_argument('--from', dest='from_', type=not_empty_string("from"),
                        help='Sender email address', required=True)
    parser.add_argument('--recipients', nargs='+', type=email_type("recipients"),
                        help='Recipient email addresses', required=True)
    parser.add_argument('--subject', type=not_empty_string("subject"),
                        help='Email subject', required=True)
    parser.add_argument('--email-text', type=not_empty_string("email-text"),
                        help='Email body text', required=True)

    args = parser.parse_args()

    send_mail(
        smtp_address=args.smtp_address, smtp_port=args.smtp_port,
        smtp_login=args.smtp_login, smtp_password=args.smtp_password,
        from_=args.from_, recipients=args.recipients,
        subject=args.subject, email_text=args.email_text
    )


if __name__ == "__main__":
    main()


