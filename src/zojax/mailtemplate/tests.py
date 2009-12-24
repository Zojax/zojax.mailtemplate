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
import unittest, doctest
from zope import component, interface
from zope.app.testing import setup
from zope.component import testing
from zope.sendmail.mailer import SMTPMailer

from zojax.mail.mailer import Mailer
from zojax.mail.default import DefaultFromAddress, DefaultErrorsAddress
from zojax.mail.interfaces import IMessage, IMailer, IMailDebugSettings

from zojax.mailtemplate import template
from zojax.mailtemplate.generator import MailGenerator
from zojax.mailtemplate.mailer import FromHeaders, ToHeaders, ErrorsHeaders

emails = []

tmpl = template.MailPageTemplate('tests_text.pt')


def send(self, fromaddr, toaddr, message):
    emails.append((fromaddr, toaddr, message))


def getEMails(clear=True):
    global emails
    m = list(emails)
    if clear:
        emails = []
    return m


class DebugSettings(object):
    interface.implements(IMailDebugSettings)

    disabled = False
    log_emails = False
    no_delivery = False


def setUp(test):
    testing.setUp(test)
    setup.setUpTestAsModule(test, 'zojax.mailtemplate.TESTS')

    mailer = Mailer()
    mailer.hostname = 'localhost'
    mailer.port = 25
    mailer.username = ''
    mailer.password = ''
    mailer.email_from_name = u'Portal administrator'
    mailer.email_from_address = u'portal@zojax.net'
    mailer.errors_address = 'errors@zojax.net'
    SMTPMailer.send = send
    component.provideUtility(mailer, IMailer)
    component.provideUtility(DebugSettings())
    component.provideAdapter(DefaultFromAddress)
    component.provideAdapter(DefaultErrorsAddress)

    component.provideAdapter(ToHeaders, name='to')
    component.provideAdapter(FromHeaders, name='from')
    component.provideAdapter(ErrorsHeaders, name='errors')

    component.provideAdapter(MailGenerator)
    component.provideAdapter(MailGenerator, provides=IMessage)


def tearDown(test):
    testing.tearDown(test)
    del SMTPMailer.send

    setup.tearDownTestAsModule(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'tests.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
