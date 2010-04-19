from interfaces import *
from persistent import Persistent
from zc.async.interfaces import IQueue
from zc.async.job import Job
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import adapts, adapter, getSiteManager, implementedBy, adaptedBy
from zope.interface import implements, implementer
from zope.traversing.api import getRoot
from zope.traversing.browser.absoluteurl import SiteAbsoluteURL
import gdata
import gdata.youtube
import gdata.youtube.service
import os
import zope.annotation


class YoutubeBase(object):
    """Base class for Adapters providing IYoutube for IYoutubeable objects
    Subclasses should only implement the upload() method.
    """
    def __init__(self, context):
        self.context = context
        self.service = gdata.youtube.service.YouTubeService()
        self.globalconfig = IGlobalConfig(context)
        self.localconfig = ILocalConfig(context)
        self.service.developer_key = self.globalconfig.developer_key
        self.service.client_id = self.globalconfig.client_id
        self.auth_token = self.localconfig.auth_token

    def get_auth_link(self, request):
        next = SiteAbsoluteURL(self.context, request)()
        scope = 'http://gdata.youtube.com'
        secure = False
        session = True
        return self.service.GenerateAuthSubURL(next, scope, secure, session).to_string()

    def authenticate(self, request):
        """Authenticate against youtube services
        """
        # set the stored token if we have one
        if self.auth_token != '':
            self.service.SetAuthSubToken(self.auth_token)
        elif 'token' in request:
            url = request.getURL() + str(request.get('QUERY_STRING'))
            token = gdata.auth.extract_auth_sub_token_from_url(url)
            self.service.UpgradeToSessionToken(token)
            self.localconfig.auth_token = token.get_token_string()

    def is_authenticated(self):
        """we are considered authenticated if we have a token
        """
        return self.auth_token != ''

    def get_video(self):
        raise NotImplementedError

    def upload(self):
        """The method that launches the upload and returns the job
        """
        queue = IQueue(self.context)
        job = queue.put(Job(self._uploader))
        # store the job for monitoring
        self.localconfig.job = job
        return job

    def _uploader(self):
        """really do the upload
        """
        # the video must be a path or a file-like object (with read())
        video, title, description, keywords, geolocation = self.get_video()

        group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain',
                                                text=description),
            keywords=gdata.media.Keywords(text=keywords),
            category=[gdata.media.Category(
                text='Autos',
                scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                label='Tests')],
            player=None
        )


        #prepare a geo.where object to hold the geographical location of where the video was recorded
        where = gdata.geo.Where()
        where.set_location(geolocation)

        # create the gdata.youtube.YouTubeVideoEntry to be uploaded
        video_entry = gdata.youtube.YouTubeVideoEntry(media=group, geo=where)

        try:
            new_entry = self.service.InsertVideoEntry(video_entry, video)
        except gdata.youtube.service.YouTubeError, e:
            print e
        self.localconfig.youtube_link = new_entry.link[0].href


class GlobalConfig(Persistent):
    """annotation adapter
    """
    adapts(IAttributeAnnotatable)
    implements(IGlobalConfig)

    developer_key = ''
    client_id = ''

from zope.annotation import factory as annotationfactory

def globalconfigfactory(factory):
    """wrapper for the annotation factory, to use the nearest sitemanager
    as a context
    """
    adapts = adaptedBy(factory)
    if adapts is None:
        raise TypeError("Missing 'zope.component.adapts' on annotation")

    @adapter(list(adapts)[0])
    @implementer(list(implementedBy(factory))[0])
    def getAnnotation(context):
        return annotationfactory(factory)(getSiteManager(context))

    getAnnotation.factory = factory
    return getAnnotation

class LocalConfig(Persistent):
    """annotation adapter
    """
    adapts(IAttributeAnnotatable)
    implements(ILocalConfig)

    auth_token = ''
    job = None
    youtube_link = ''


globalconfig = globalconfigfactory(GlobalConfig)
localconfig = zope.annotation.factory(LocalConfig)


class TestYoutube(YoutubeBase):
    """An implementation of the adapter for tests
    """
    adapts(IYoutubeable)
    implements(IYoutube)

    def get_video(self):
        title = 'test'
        description = 'test upload'
        keywords = 'test'
        geolocation = (37.0,-122.0)

        import aws.youtube
        path = os.path.join(os.path.dirname(aws.youtube.adapters.__file__),
                            'sample.ogg')
        return path, title, description, keywords, geolocation








