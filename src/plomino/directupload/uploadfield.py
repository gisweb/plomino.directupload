# -*- coding: utf-8 -*-
#
# File: attachment.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

# Zope
from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.schema import getFields, Choice, TextLine
from zope.schema.vocabulary import SimpleVocabulary

# CMF / Archetypes / Plone
from Products.CMFPlone.utils import normalizeString

# Plomino
from Products.CMFPlomino.fields.base import IBaseField, BaseField, BaseForm
from Products.CMFPlomino.interfaces import IPlominoField
from Products.CMFPlomino.fields.dictionaryproperty import DictionaryProperty
from ZPublisher.HTTPRequest import FileUpload
from iol.document.config import ICONxCONTENT, SMALLICONxCONTENT


class IUploadField(IBaseField):
    """ Attachment field schema
    """
    widget = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Single file", "SINGLE"), ("Multiple files", "MULTI")]),
                title=u'Type',
                description=u'Single, multiple file(s) or download->upload',
                default="MULTI",
                required=True)

    maxsize = TextLine(
            title=u'Max size',
            description=u'File max size allowed (Mb)',
            required=False)

    filetype = TextLine(
            title=u'File type',
            description=u'File type allowed (separate comma list)',
            required=False)

    printservice = TextLine(
            title=u'Print Service',
            description=u'Create document service ',
            required=False)



class UploadField(BaseField):
    """
    """
    implements(IUploadField)

    plomino_field_parameters = {'interface': IUploadField,
                                'label':"File upload",
                                'index_type':"ZCTextIndex"}

    read_template = PageTemplateFile('browser/templates/upload_read.pt')
    edit_template = PageTemplateFile('browser/templates/upload_edit.pt')    
    fieldValue = None

    def getIcon(self, content_type, size='big'):
        if size=='big':
            config = ICONxCONTENT
        else:
            config = SMALLICONxCONTENT

        if content_type in config:
            return config[content_type]
        else:
            return config["default"]

    def validate(self, submittedValue):
        """
        """
        errors=[]
        fieldname = self.context.id
        doc = self.getDocument()
        v = doc.getItem(fieldname)
        if self.context.getMandatory() and not v:
            field = doc.getForm().getFormField(fieldname)
            errors = ["Manca il valore del campo %s" %field.title]

        return errors


    def getDocument(self):
        """
        """
        docId = self.context.REQUEST["URL1"].split('/')[-1]
        db = self.context.getParentDatabase()
        doc = db.getDocument(docId)
        return doc


    def processInput(self, submittedValue):
        """
        """
        if submittedValue == 'pass':
            doc = self.getDocument()
            fieldname = self.context.id
            v = doc.getItem(fieldname,None)
            return v



    @property
    def Pippo(self):
        return "PIPPO"
       

component.provideUtility(UploadField, IPlominoField, 'UPLOAD')

for f in getFields(IUploadField).values():
    setattr(UploadField,
            f.getName(),
            DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IUploadField)