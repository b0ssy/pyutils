import os
from logging import getLogger
import time
from dotenv import load_dotenv
import requests

from utils import SMTPClient, configure_logs


load_dotenv()

LOG = getLogger("pyutils")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 300))
CHECK_URLS = os.environ["CHECK_URLS"].split("|")
NOTIFY_EMAILS = os.environ["NOTIFY_EMAILS"].split("|")

smtp = SMTPClient(
    host=os.environ["EMAIL_SMTP_DOMAIN"],
    port=os.environ["EMAIL_PORT"],
    username=os.environ["EMAIL_USERNAME"],
    password=os.environ["EMAIL_PASSWORD"],
    alias=os.environ["EMAIL_ALIAS"],
)


def main():
    check_urls_flags = dict()
    for check_url in CHECK_URLS:
        check_urls_flags[check_url] = True

    while True:
        try:
            for check_url in CHECK_URLS:
                # GET url
                success = False
                try:
                    LOG.info(f"GET: {check_url}")
                    requests.get(check_url)
                    success = True
                    LOG.info(f"GET: {check_url} succesfully")
                except KeyboardInterrupt as ex:
                    raise ex
                except Exception as ex:
                    LOG.error(f"Failed to GET {check_url}: {ex}")
                
                # Send emails if needed
                try:
                    if success and not check_urls_flags[check_url]:
                        LOG.info(f"UP: {check_url}")
                        LOG.info("Sending email")
                        msg = smtp.make_msg(subject=f"UP: {check_url}", html="")
                        smtp.send_tls(msg, recipient_emails=NOTIFY_EMAILS)
                        check_urls_flags[check_url] = True
                        LOG.info("Sent email successfully")
                    elif not success and check_urls_flags[check_url]:
                        LOG.error(f"DOWN: {check_url}")
                        LOG.info("Sending email")
                        msg = smtp.make_msg(subject=f"DOWN: {check_url}", html="")
                        smtp.send_tls(msg, recipient_emails=NOTIFY_EMAILS)
                        check_urls_flags[check_url] = False
                        LOG.info("Sent email successfully")
                except KeyboardInterrupt as ex:
                    raise ex
                except Exception as ex:
                    LOG.error(f"Failed to send emails: {ex}")

            LOG.info(f"Checking again in {CHECK_INTERVAL_SECONDS} seconds")
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt as ex:
            raise ex
        except Exception as ex:
            LOG.error(f"Exception: {ex}")


if __name__ == "__main__":
    configure_logs()
    main()
