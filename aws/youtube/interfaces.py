from zope.interface import Interface
from zope.annotation.interfaces import IAttributeAnnotatable

class IYoutubeable(IAttributeAnnotatable):
    """Marker interface for objects that can be uploaded to youtube,
    typically video blob (or non blob) objects
    """

class IYoutubeAnnotations(Interface):
    """Interface of the annotation adapter
    """

class IYoutube(Interface):
    """Interface of the Youtube features
    """

