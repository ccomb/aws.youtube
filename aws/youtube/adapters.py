from interfaces import IYoutube, IYoutubeable
from persistent import Persistent
from zope.component import adapts
from zope.interface import implements
import zope.annotation

class Youtube(Persistent):
    """Adapter providing IYoutube for IYoutubeable objects
    """
    adapts(IYoutubeable)
    implements(IYoutube)
    auth_token = None

    def authenticate(self):
        """Authenticate against youtube services
        """

youtubefactory = zope.annotation.factory(Youtube)

