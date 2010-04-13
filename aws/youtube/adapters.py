from interfaces import *
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.annotation.interfaces import IAttributeAnnotatable
from persistent import Persistent
from zope.component import adapts, getSiteManager
from zope.interface import implements
import gdata.youtube.service
import os
import zope.annotation
from zope.traversing.api import getRoot


class Youtube(object):
    """Adapter providing IYoutube for IYoutubeable objects
    """
    adapts(IYoutubeable)
    implements(IYoutube)
    auth_token = None

    def __init__(self, context):
        self.context = context
        self.service = gdata.youtube.service.YouTubeService()
        mainconfig = IYoutubeAnnotations(getSiteManager(context))
        self.service.developer_key = mainconfig.developer_key
        self.service.client_id = mainconfig.client_id

    def get_auth_link(self, request):
        next = AbsoluteURL(self.context, request)
        scope = 'http://gdata.youtube.com'
        secure = False
        session = True
        return self.service.GenerateAuthSubURL(next, scope, secure, session)

    def authenticate(self):
        """Authenticate against youtube services
        """

class YoutubeAnnotations(Persistent):
    """annotation adapter
    """
    adapts(IAttributeAnnotatable)
    implements(IYoutubeAnnotations)

    developer_key = ''
    client_id = ''



youtubeannotations = zope.annotation.factory(YoutubeAnnotations)

