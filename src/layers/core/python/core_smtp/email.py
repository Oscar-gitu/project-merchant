# -*- coding: utf-8 -*-
"""
email send service library. Using SMTP.
"""
import datetime
import logging
import mimetypes
import os
import smtplib
from email import encoders
from email.header import Header
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import (
    MIMEMultipart,
)
from email.mime.text import MIMEText

from core_aws.ssm import (
    get_parameter,
)

__all__ = ["send_email_tigo"]


def _get_attach_msg(path):
    """make MIME type attachment message"""
    if not os.path.isfile(path):
        return
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    if maintype == "text":
        fp = open(path)
        # Note: we should handle calculating the charset
        msg = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(path, "rb")
        msg = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(path, "rb")
        msg = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(path, "rb")
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        encoders.encode_base64(msg)
    # Set the filename parameter
    msg.add_header("Content-Disposition", "attachment", filename=path.split("/")[-1])
    return msg


def _make_mime(mail_from, mail_to, subject, body, attachments):
    """create MIME"""
    msg = MIMEMultipart()
    msg["From"] = Header(mail_from, "ascii")
    msg["To"] = Header(mail_to, "ascii")
    msg["Subject"] = Header(subject, "ascii")
    msg.preamble = "You will not see this in a MIME-aware mail reader.\n"
    msg.attach(MIMEText(body, "html"))
    for filepath in attachments:
        msg.attach(_get_attach_msg(filepath))
    return msg


def send_email(
    sender, receivers, subject, content, attachments, smtp_host, smtp_user, smtp_passwd
):
    """
    Send email using smtp server and auth
    param:
    sender: email sender address
    receiver: email receiver addresses list, eg. ['alice@example.com']
    subject: email title string
    content: email content string
    smtp_host: smtp host address
    smtp_user: smtp user name
    smtp_passwd: smtp password
    """
    try:
        client = smtplib.SMTP(smtp_host, 587)
        client.ehlo()
        client.starttls()
        client.ehlo()
        client.login(smtp_user, smtp_passwd)

        client.sendmail(
            sender,
            receivers,
            _make_mime(
                sender, ",".join(receivers), subject, content, attachments
            ).as_string(),
        )
        client.quit()

        logging.debug("Successfully sent email")
        return "Successfully sent email"
    except smtplib.SMTPException as e:
        logging.warning("Error: unable to send email")
        logging.warning(f"Unable to send email to {sender}: {e}")


def send_email_tigo(sender, receivers, subject, content, attachments):
    import core_utils.environment

    SMTP_HOST = core_utils.environment.SMTP_HOST or get_parameter(
        f"SMTPHost_{core_utils.environment.ENVIRONMENT.lower()}", is_dict=False
    )
    SMTP_USER = core_utils.environment.SMTP_USER or get_parameter(
        f"SMTPUser_{core_utils.environment.ENVIRONMENT.lower()}", is_dict=False
    )
    SMTP_PASSWD = core_utils.environment.SMTP_PASSWD or get_secret_parameter(
        f"SMTPPassword_{core_utils.environment.ENVIRONMENT.lower()}", is_dict=False
    )

    return send_email(
        sender,
        receivers,
        subject,
        content,
        attachments,
        SMTP_HOST,
        SMTP_USER,
        SMTP_PASSWD,
    )
