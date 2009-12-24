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
from email.Utils import formataddr

from zope import interface
from zope.component import queryUtility, queryMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate
from zojax.mail.interfaces import IMailer, IDestinationAddress

from utils import wrap_filename
from generator import IMailMessage
from interfaces import IMailTemplate


class MailTemplateBase(object):
    """ mail template with base features """
    interface.implements(IMailTemplate)

    subject = u''
    charset = u'utf-8'
    contentType = u'text/plain'
    messageId = None
    template = None

    def __init__(self, context, *args):
        super(MailTemplateBase, self).__init__(context, *args)

        self.context = context
        self.request = args[-1]

        args = args[:-1]
        self.contexts = args

        for idx in range(len(args)):
            setattr(self, 'context%s'%idx, args[idx])

        self._files = []
        self._headers = {}
        self._alternative = []

    def addHeader(self, header, value, encode=False):
        self._headers[header] = (header, value, encode)

    def hasHeader(self, header):
        header = header.lower()
        for key in self._headers.keys():
            if key.lower() == header:
                return True

        return False

    def getHeaders(self):
        return self._headers.values()

    def addAttachment(self, file_data, content_type,
                      filename, disposition='attachment'):
        self._files.append((file_data, content_type,
                            wrap_filename(filename), disposition))

    def getAttachments(self):
        return self._files

    def addAlternative(self, template):
        self._alternative.append(template)

    def getAlternative(self):
        return self._alternative

    def update(self):
        pass

    def render(self):
        template = queryMultiAdapter((self, self.request), IPageTemplate)
        if template is not None:
            return template(self)

        return self.template()

    def send(self, emails, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

        self.to_address = emails
        interface.directlyProvides(self, IDestinationAddress)

        mailer = queryUtility(IMailer)
        if mailer is not None:
            mailer.sendmail(self)

    def __call__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

        return IMailMessage(self)()
