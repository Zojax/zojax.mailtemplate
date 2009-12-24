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
""" zojax.mailtemplate interfaces

$Id$
"""
from zope import interface


class IMailMessage(interface.Interface):
    """ email message """

    def __call__():
        """ return message as string """

    def message():
        """ return email object """


class IMailHeaders(interface.Interface):
    """ mail headers ,
        hreader - Tuple of (header_name, header_value, encode) """

    headers = interface.Attribute('Headers')


class IMailTemplate(interface.Interface):
    """ mail template """

    charset = interface.Attribute('Charset')

    contentType = interface.Attribute('Message content type')

    messageId = interface.Attribute('Unique Message ID')

    template = interface.Attribute('Template')


    def __init__(context, request):
        """ multi adapter """

    def addHeader(header, value, encode=False):
        """ add header to teamplte,
            encode is true use make_header from email package """

    def addAlternative(template):
        """ add alternative mail template """

    def hasHeader(header):
        """ check header """

    def getHeaders():
        """ extra headers, (header_name, value, encode) """

    def addAttachment(file_data, content_type, filename):
        """ add attachment """

    def getAttachments():
        """ extra attachments, (file_data, content_type, filename, disposition) """

    def getAlternative():
        """ alternative """

    def update():
        """ update mailtemplate """

    def render():
        """ render mailtemplate and return results """

    def send(emails, **kw):
        """ generate email and send to emails, kw set as attributes """

    def __call__(**kw):
        """ update template and render, kw set as attributes """
