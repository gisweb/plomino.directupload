# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.CMFPlone.utils import safe_unicode
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.api.env import adopt_roles

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from collective.upload.config import IMAGE_MIMETYPES
from ..config import ATTACHMENT_FOLDER, ICONxCONTENT
import json
import base64
from Products.CMFPlone.utils import normalizeString
from ZPublisher.HTTPRequest import FileUpload
from plone.memoize.view import memoize
from ..uploadfield import IUploadField

try:
    from plone.app.blob.field import BlobWrapper
    from plone.app.blob.utils import guessMimetype
    HAS_BLOB = True
except ImportError, e:
    HAS_BLOB = False



class Attachments(BrowserView):
    field = None
    ErrorMessage = None

    def publishTraverse(self, request, fieldName):
        if fieldName:
            self.fieldName = fieldName
            form = self.doc.getForm()
            field = form.getFormField(self.fieldName)
            if field:
                self.field = field
                self.settings = field.getSettings()
                self.fieldTitle = field.title

        return self

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doc = context
        #multi = self.multi# =  "multi" in request.keys()

    @property
    @memoize
    def multi(self):
        return self.settings.widget=='MULTI'
    
    def removeAttachment(self):
        """
        """
        filename = self.request.get("filename")
        current_files = self.doc.getItem(self.fieldName)
        if current_files.has_key(filename):
            del current_files[filename]
            self.setItem(fieldname, current_files)
            self.deletefile(filename)
        self.request.RESPONSE.setHeader('content-type', 'application/json; charset=utf-8')
        return json.dump(current_files)


    #usata per le prove
    def getAttachmentFiles(self):
        self.request.RESPONSE.setHeader('content-type', 'application/json; charset=utf-8')
        return filesInfo(self.doc, self.fieldName)


    def getAttachmentUrl(self):
        """
        url dell'allegato
        """
        docfolderId = self.doc.getId()
        dbfolderId = self.doc.getParentDatabase().id
        target = self.context.portal_url.getPortalObject()[ATTACHMENT_FOLDER][dbfolderId][docfolderId]
        return target.absolute_url_path()


    def __call__(self):
        #multi=self.multi
        if hasattr(self.request, 'REQUEST_METHOD'):
            # TODO: we should check errors in the creation process, and
            # broadcast those to the error template in JS
            if self.request['REQUEST_METHOD'] == 'POST':
                if getattr(self.request, 'files[]', None) is not None:
                    files = self.request['files[]']
                    title = self.request['title[]']
                    description = self.request['description[]']
                    uploaded = self.upload([files], [title], [description])
                    if uploaded:
                        return json.dumps({'files': uploaded})
                return ""

        if not self.field:
            self.ErrorMessage =  "Manca il campo %s" %self.fieldName
        elif not IUploadField.providedBy(self.settings):
            self.ErrorMessage =  "Il campo %s non è di tipo Direct Upload" %self.fieldName

        if self.ErrorMessage:
            errorDialog = ViewPageTemplateFile("templates/error_dialog.pt")
            return errorDialog(self)

        return self.index()

    def upload(self, files, title='', description=''):

        if not self.doc.isDocument():
            return


        #import pdb;pdb.set_trace()

        overwrite = True

        current_files = self.doc.getItem(self.fieldName,{})
        if not current_files:
            current_files = dict()


        #Utile ma pericoloso: se cambio da multi a single elimino tutti i file.. da vedere 
        # if not self.multi:
        #     for fileId in current_files.keys():
        #         self.doc.deletefile(fileId)

        if not isinstance(files, list):
            files = [files]

        namechooser = INameChooser(self.doc)
        info = {'name': 'File-Name.jpg',
                'title': '',
                'description': '',
                'size': 999999,
                'url': '@@getattachment?',
                'thumbnail_url': '//nohost.org',
                'delete_url': '//nohost.org',
                'delete_type': 'DELETE',
                'field_name': self.fieldName
                }

        results = []

        for item in files:
            if item.filename:

    #            if overwrite and filename in self.objectIds():
    #                self.doc.deletefile(filename)

                contenttype = item.headers.get('Content-Type')
                filename = safe_unicode(item.filename)
                data = item.read()
                id_name = ''
                title = title and title[0] or filename
                #non usata
                description = description and description[0] or ''

                # Get a unique id here
                id_name = namechooser.chooseName(title, self.doc)

                info["name"] = id_name
                info["title"] = title
                info["description"] = description
                info["thumbnail_url"] = self.getIcon(contenttype)
                info["content_type"] = contenttype

                try:
                    blob = BlobWrapper(contenttype)
                except:  # XXX Except what?
                    # BEFORE PLONE 4.0.1
                    blob = BlobWrapper()

                file_obj = blob.getBlob().open('w')
                file_obj.write(data)
                file_obj.close()
                blob.setFilename(id_name)
                blob.setContentType(contenttype)
                info['size'] = blob.get_size()
                self.doc._setObject(id_name, blob)          
                results.append(info)


                if self.settings.widget=='MULTI':
                    current_files[id_name] = contenttype
                    self.doc.setItem(self.fieldName,current_files)
                else:
                    self.doc.setItem(self.fieldName,{id_name:contenttype})

            if results:
                return results
            return False





    def getIcon(self, content_type, size='big'):
        if size=='big':
            config = ICONxCONTENT
        else:
            config = SMALLICONxCONTENT

        if content_type in config:
            return config[content_type]
        else:
            return config["default"]


    def getFileInfo(self, item):
        context_type = 'File'
        info = {'name': 'adasd',
                'title': 'asdasdasd',
                'description': 'asdasdasd',
                'url': 'sdasda',
                'delete_url': 'adsdasda',
                'delete_type': 'DELETE',
                'field_name' : 'sadasd',
                }

        if hasattr(item, 'size'):
            info['size'] = context.size()
        else:
            if context_type == 'File':
                info['size'] = context.file.getSize()
            elif context_type == 'Image':
                info['size'] = context.image.getSize()
        if context_type == 'Image':
            scales = context.restrictedTraverse('@@images')
            thumb = scales.scale(element='image', scale='thumb')
            info['thumbnail_url'] = thumb.url
        return info

    def folderupload(self, files, title='', description=''):


        if not self.doc.isDocument():
            return


        self.doc.setfile(self.doc, files[0])


        docfolderId = self.doc.getId()
        dbfolderId = self.doc.getParentDatabase().id

        #TODO come configurare diverse cartelle per applicazione o plomino db (da fare sulle singole app)?
        target = self.context.portal_url.getPortalObject()[ATTACHMENT_FOLDER]

        with adopt_roles('Manager'):
            if not dbfolderId in target.keys():
                target.invokeFactory("Folder", id=dbfolderId, title=dbfolderId)
            target = target[dbfolderId]
            if not docfolderId in target.keys():
                target.invokeFactory("Folder", id=docfolderId, title=docfolderId)
            docFolder = target[docfolderId]
            for username, roles in self.doc.get_local_roles():
                docFolder.manage_setLocalRoles(username, roles)

        if not isinstance(files, list):
            files = [files]

        #se non  campo multiplo vuoto la cartella
        #TODO tenere allineati i files nella cartella con i nomi sul campo di plomino 
        current_files = self.doc.getItem(self.element)
        cleaned_files = {}
        if self.multiple:
            for fName in current_files:
                if fName in docFolder.keys():
                    cleaned_files[fName] = current_files[fName]
            self.doc.setItem(self.element, cleaned_files)

        #se upload singolo cancello tutti i file presenti collegati al campo
        else:
            try:
                docFolder.manage_delObjects(current_files.keys())
            except Exception as error:
                pass
            self.doc.removeItem(self.element)     

        namechooser = INameChooser(docFolder)
        loaded = []
        for item in files:
            if item.filename:
                content_type = item.headers.get('Content-Type')
                filename = safe_unicode(item.filename)
                data = item.read()
                id_name = ''
                title = title and title[0] or filename
                # Get a unique id here
                id_name = namechooser.chooseName(title, docFolder)

                # Portal types allowed : File and Image
                # Since Plone 4.x both types use Blob
                if content_type in IMAGE_MIMETYPES:
                    portal_type = 'Image'
                    wrapped_data = NamedBlobImage(data=data, filename=filename)
                else:
                    portal_type = 'File'
                    wrapped_data = NamedBlobFile(data=data, filename=filename)

                # Create content
                docFolder.invokeFactory(portal_type,
                                           id=id_name,
                                           title=title,
                                           description=description[0])



                newfile = docFolder[id_name]
                # Set data
                if portal_type == 'File':
                    if IATFile.providedBy(newfile):
                        newfile.setFile(data, filename=filename)
                    else:
                        newfile.file = wrapped_data
                elif portal_type == 'Image':
                    if IATImage.providedBy(newfile):
                        newfile.setImage(data, filename=filename)
                    else:
                        newfile.image = wrapped_data

                # Finalize content creation, reindex it
                newfile.reindexObject()
                notify(ObjectModifiedEvent(newfile))
                loaded.append(newfile)
            if loaded:
                return loaded
            return False
