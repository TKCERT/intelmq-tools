# -*- coding: utf-8 -*-
"""
Uses the common mail iteration method from the lib file.
"""
from intelmq.bots.collectors.mail.lib import MailCollectorBot
from email import message_from_string


class MailPartCollectorBot(MailCollectorBot):

    def init(self):
        super().init()

        self.content_types = getattr(self.parameters, 'content_types', ('text/plain', 'text/html'))
        if isinstance(self.content_types, str):
            self.content_types = [x.strip() for x in self.content_types.split(',')]
        elif not self.content_types or self.content_types is True:  # empty string, null, false, true
            self.content_types = ('text/plain', 'text/html')

    def process_message(self, uid, message):
        seen = False

        email_message = message_from_string(message.raw_email)
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() in self.content_types:
                    report = self.new_report(message, part.get_content_type())
                    report["raw"] = str(part).split('\n\n', 1)[1]
                    self.send_message(report)
                    seen = True

        elif email_message.get_content_type() in self.content_types:
            report = self.new_report(message, email_message.get_content_type())
            report["raw"] = str(email_message)
            self.send_message(report)
            seen = True

        return seen

    def new_report(self, message, content_type):
        report = super().new_report()
        report["extra.email_subject"] = message.subject
        report["extra.email_from"] = ','.join(x['email'] for x in message.sent_from)
        report["extra.email_message_id"] = message.message_id
        report["extra.email_content_type"] = content_type

        return report


BOT = MailPartCollectorBot
