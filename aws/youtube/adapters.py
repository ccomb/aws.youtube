from interfaces import *
from persistent import Persistent
from zope.component import adapts
from zope.interface import implements
import zope.annotation

class Youtube(object):
    """Adapter providing IYoutube for IYoutubeable objects
    """
    adapts(IYoutubeable)
    implements(IYoutube)
    auth_token = None

    def __init__(self, context):
        self.context = context

    def get_auth_link(self):
        pass

    def authenticate(self):
        """Authenticate against youtube services
        """

class YoutubeAnnotations(Persistent):
    """annotation adapter
    """
    adapts(IYoutubeable)
    implements(IYoutubeAnnotations)



youtubeannotations = zope.annotation.factory(YoutubeAnnotations)

