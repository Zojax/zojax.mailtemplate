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
import os.path
from zope import schema, interface
from zope.component.zcml import handler
from zope.configuration import fields, exceptions
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from base import MailTemplateBase
from template import MailPageTemplate
from interfaces import IMailTemplate


class IMailTemplateDirective(interface.Interface):
    """A directive to register a new mailtemplate.

    The mailtemplate directive also supports an
    undefined set of keyword arguments that are set as mailtemplate headers.
    """

    for_ = fields.Tokens(
        title = u"Context",
        description = u"The content interface or class this mail template is for.",
        value_type = fields.GlobalObject(missing_value=object()),
        required = True)

    name = schema.TextLine(
        title = u"The name of the pagelet.",
        description = u"The name shows up in URLs/paths. For example 'foo'.",
        required = False)

    subject = schema.TextLine(
        title = u"Message subject",
        required = False)

    charset = schema.ASCIILine(
        title = u"Message charset",
        default = 'utf-8',
        required = False)

    contentType = schema.TextLine(
        title = u"Message content type",
        default = u'text/plain',
        required = False)

    class_ = fields.GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the mailtemplate.",
        required=False)

    provides = fields.Tokens(
        title = u'Provides',
        required = False,
        value_type = fields.GlobalInterface())

    template = fields.Path(
        title = u'Mailtemplate template.',
        description = u"Refers to a file containing a page template (should "\
                                "end in extension ``.pt`` or ``.html``).",
        required=False)

    layer = fields.GlobalObject(
        title = u'Layer',
        description = u'The layer for which the template should be available',
        required = False,
        default=IDefaultBrowserLayer)

# Arbitrary keys and values are allowed to be passed to the pagelet.
IMailTemplateDirective.setTaggedValue('keyword_arguments', True)


# pagelet directive
def mailTemplateDirective(
    _context, for_, name='', subject='', charset='utf-8',
    contentType='text/plain', class_=None, provides=(IMailTemplate,),
    template=u'', layer=IDefaultBrowserLayer, **kwargs):

    # Make sure that the template exists
    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise exceptions.ConfigurationError("No such file", template)
        kwargs['template'] = MailPageTemplate(template)

    # Build a new class that we can use different permission settings if we
    # use the class more then once.
    cdict = {}
    cdict.update(kwargs)
    cdict['__name__'] = name
    cdict['charset'] = charset
    cdict['contentType'] = contentType

    if subject:
        cdict['subject'] = subject

    if class_ is not None:
        bases = (class_, MailTemplateBase)
    else:
        bases = (MailTemplateBase,)

    Class = type('MailTemplateClass from %s'%class_, bases, cdict)

    interface.classImplements(Class, provides)

    for_.append(layer)

    # register mailtemplate
    for iface in provides:
        _context.action(
            discriminator = ('zojax:mailtemplate', tuple(for_), name, iface),
            callable = handler,
            args = ('registerAdapter',
                    Class, for_, iface, name, _context.info))
