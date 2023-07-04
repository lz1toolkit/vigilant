#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import traceback
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

smtp_server = "mail.staff.sina.com.cn"


class Mail:

    def __init__(self, from_address, password):
        self.from_address = from_address
        self.password = password

    def send_html(self, to_list, cc_list, subject, content, file_list=None):

        mime_text = MIMEText(content, 'html', 'utf-8')

        if file_list:
            msg = MIMEMultipart()
            msg.attach(mime_text)

            for f in file_list:
                ma = MIMEApplication(open(f, 'rb').read())
                f_n = f
                if os.path.sep in f:
                    f_n = f[f.rindex(os.path.sep) + 1:]
                ma.add_header('Content-Disposition', 'attachment', filename='%s' % f_n)
                msg.attach(ma)
        else:
            msg = mime_text

        msg["from"] = self.from_address
        msg["to"] = ",".join(to_list)
        msg["cc"] = ",".join(cc_list)
        msg["Subject"] = subject

        try:
            server = smtplib.SMTP(host=smtp_server, port=587)
            server.starttls()
            server.set_debuglevel(1)
            receive = to_list
            receive.extend(cc_list)
            server.login(self.from_address.split("@")[0], self.password)
            server.sendmail(self.from_address, receive, msg.as_string())
            server.quit()
            return True
        except smtplib.SMTPException:
            traceback.print_exc()
            return False


if __name__ == "__main__":
    pass
