##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from email.Utils import formatdate
from email.Header import make_header
from email.Charset import Charset

from zope import interface, component
from zope.component import getAdapters

from interfaces import IMailMessage, IMailHeaders, IMailTemplate


class MailGenerator(object):
    """ mail generator """
    component.adapts(IMailTemplate)
    interface.implements(IMailMessage)

    def __init__(self, context):
        self._headers = {}
        self.context = context

        context.update()

    def _addHeader(self, header, value, encode=False):
        self._headers[header] = (header, value, encode)

    def setHeaders(self, message):
        charset = str(self.context.charset)

        extra = list(self.context.getHeaders())
        for key, val, encode in self._headers.values() + extra:
            if encode:
                message[key] = make_header(((val, charset),))
            else:
                message[key] = val

    def getMessage(self):
        """ render a mail template """
        context = self.context

        charset = str(context.charset)
        contentType = context.contentType

        mail_body = context.render()
        maintype, subtype = contentType.split('/')

        message = MIMEText(
            mail_body.encode(charset), subtype, charset)

        return message

    def getAttachments(self):
        attachments = []

        # attach files
        for data, content_type, filename, disposition in \
                self.context.getAttachments():
            maintype, subtype = content_type.split('/')

            msg = MIMENonMultipart(maintype, subtype)

            msg.set_payload(data)
            if filename:
                msg['Content-Id'] = '<%s@zojax>' % filename
                msg['Content-Disposition'] = '%s; filename="%s"' % (
                    disposition, filename)

            Encoders.encode_base64(msg)

            attachments.append(msg)

        return attachments

    def message(self, multipart_format='mixed', *args, **kw):
        context = self.context

        # generate message
        message = self.getMessage()

        # generate attachments
        attachments = self.getAttachments()
        if attachments:
            # create multipart message
            root = MIMEMultipart(multipart_format)

            # insert headers
            self.setHeaders(root)

            # create message with attachments
            related = MIMEMultipart('related')
            related.attach(message)

            for attach in attachments:
                disposition = attach['Content-Disposition'].split(';')[0]
                if disposition == 'attachment':
                    root.attach(attach)
                else:
                    related.attach(attach)

            root.attach(related)
            message = root

        # alternative
        alternatives = self.context.getAlternative()
        if alternatives:
            mainmessage = MIMEMultipart('alternative')
            mainmessage.attach(message)

            for msg in alternatives:
                mainmessage.attach(IMailMessage(msg).message(
                        multipart_format, *args, **kw))

            message = mainmessage

        # default headers
        self._addHeader('Subject', context.subject, True)

        self.setHeaders(message)
        return message

    def __call__(self, multipart_format='mixed', *args, **kw):
        context = self.context
        message = self.message(multipart_format, *args, **kw)

        message['Date'] = formatdate()
        message['Message-ID'] = context.messageId

        if not message.has_key('X-Mailer'):
            message['X-mailer'] = 'zojax.mailer'

        # update externals headers
        charset = str(context.charset)

        for name, adapter in getAdapters(
            (context, context.context), IMailHeaders):
            for name, value, encode in adapter.headers:
                if encode:
                    message[name] = make_header(((value, charset),))
                else:
                    message[name] = value

        return message.as_string()
