import os
import sys
import logging

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPClient:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        alias: str | None,
    ):
        """
        A simple and convenient SMTP client

        :param host:
            SMTP server host
        :param port:
            SMTP server port
        :param username:
            Email account username
        :param password:
            Email account password
        :param alias:
            Optional alias for sender name in place of username
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.alias = alias

    def make_msg(
        self,
        subject: str,
        html: str,
    ) -> MIMEMultipart:
        """
        Make message

        :param subject:
            Message subject
        :param html:
            Message HTML content

        :returns:
            MIMEMultipart message
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        if self.alias is not None:
            msg["From"] = self.alias
        msg.attach(MIMEText(html, "html"))
        return msg

    def send_tls(
        self,
        msg: MIMEMultipart,
        recipient_emails: str | list[str],
    ) -> None:
        """
        Send email using TLS connection

        :param msg:
            Message to send
        :param recipient_emails:
            Recipient email(s) to send the message to

        :returns:
            None
        """
        with smtplib.SMTP(host=self.host, port=self.port) as server:
            server.connect(host=self.host, port=self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.username, self.password)
            server.sendmail(self.alias, recipient_emails, msg.as_string())
            server.quit()


def configure_logs(
    filename="logs/log",
    min_level=logging.DEBUG,
    print_stdout=True,
    log_format="%(asctime)s.%(msecs)03d [%(name)-12.12s] [%(levelname)-7.7s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
):
    if filename and os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    logging.basicConfig(
        filename=filename, level=min_level, format=log_format, datefmt=datefmt
    )
    if print_stdout:
        handler = logging.StreamHandler(sys.stdout)
        if log_format:
            handler.setFormatter(logging.Formatter(log_format, datefmt))
        logging.getLogger().addHandler(handler)
