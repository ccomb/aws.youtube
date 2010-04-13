from interfaces import *
from zope.traversing.browser.absoluteurl import SiteAbsoluteURL
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
    auth_token = ''

    def __init__(self, context):
        self.context = context
        self.service = gdata.youtube.service.YouTubeService()
        self.globalconfig = IYoutubeAnnotations(getSiteManager(context))
        self.localconfig = IYoutubeAnnotations(context)
        self.service.developer_key = self.globalconfig.developer_key
        self.service.client_id = self.globalconfig.client_id

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


class YoutubeAnnotations(Persistent):
    """annotation adapter
    """
    adapts(IAttributeAnnotatable)
    implements(IYoutubeAnnotations)

    developer_key = ''
    client_id = ''
    auth_token = ''



youtubeannotations = zope.annotation.factory(YoutubeAnnotations)

