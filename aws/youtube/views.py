from interfaces import *
from zc.async.interfaces import NEW, PENDING, ASSIGNED, ACTIVE, COMPLETED
from z3c.form.field import Fields
from z3c.form.form import EditForm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest



class UploadContentProvider(object):
    """a single content provider for auth/upload/deletion
    The context should be a video file object.
    """
    implements(IContentProvider)
    adapts(IYoutubeable, IBrowserRequest)
    auth_link = ''

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.youtube = IYoutube(self.context)
        self.job = self.youtube.localconfig.job
        self.youtube_link = self.youtube.localconfig.youtube_link

    def update(self):
        if not self.youtube.is_authenticated():
            self.auth_link = self.youtube.get_auth_link(self.request)
            self.template = 'not_authenticated.pt'
        elif self.job is None:
            self.template = 'upload.pt'
        elif self.job is not None and self.job.status is not COMPLETED:
            # XXX should manage errors
            self.template = 'uploading.pt'
        elif self.job is not None and self.job.status is COMPLETED:
            self.template = 'uploaded.pt'
        else:
            raise NotImplementedError



    def render(self):
        return ViewPageTemplateFile(self.template)(self)


class Authenticate(BrowserView):
    """view that receives the authsub token
    and turn it into a permanent session token
    """
    def __call__(self):
        IYoutube(self.context).authenticate(self.request)
        self.request.response.redirect('.')


class Upload(BrowserView):
    """A view that launches an async upload
    """
    def __call__(self):
        youtube = IYoutube(self.context)
        youtube.authenticate(self.request)
        if youtube.localconfig.job is None:
            youtube.upload()
        self.request.response.redirect('.')


class GlobalConfig(EditForm):
    """EditForm to enter the dev key and app id
    It's turned into a content provider.
    """
    implements(IContentProvider)
    adapts(IYoutubeable, IBrowserRequest, Interface)
    fields = Fields(IGlobalConfig).omit('__name__', '__parent__')
    template = ViewPageTemplateFile('simple_editform.pt')
    label = u'Global parameters'






