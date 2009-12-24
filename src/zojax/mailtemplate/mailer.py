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
from zope import interface, component

from zojax.mail.interfaces import IFromAddress
from zojax.mail.interfaces import IErrorsAddress
from zojax.mail.interfaces import IDestinationAddress

from interfaces import IMailHeaders, IMailTemplate


class ErrorsHeaders(object):
    interface.implements(IMailHeaders)
    component.adapts(IMailTemplate, interface.Interface)

    headers = ()

    def __init__(self, template, context):
        # errors header
        errors = IErrorsAddress(template).errors_address
        if errors:
            self.headers = (('Errors-To', errors, False),
                            ('Return-Path', errors, False))

class ToHeaders(object):
    interface.implements(IMailHeaders)
    component.adapts(IMailTemplate, interface.Interface)

    headers = ()

    def __init__(self, template, context):
        if not template.hasHeader('to'):
            addr = IDestinationAddress(template, None)
            if addr is not None and addr.to_address:
                self.headers = (('To', addr.to_address[0], False),)
                pass


class FromHeaders(object):
    interface.implements(IMailHeaders)
    component.adapts(IMailTemplate, interface.Interface)

    headers = ()

    def __init__(self, template, context):
        if not template.hasHeader('from'):
            from_hdr = IFromAddress(template).from_address
            self.headers = (('From', from_hdr, False),)
