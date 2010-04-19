from zope.interface import Interface
from zope.schema import TextLine
from zope.interface import Attribute
from zope.annotation.interfaces import IAttributeAnnotatable

class IYoutubeable(IAttributeAnnotatable):
    """Marker interface for objects that can be uploaded to youtube,
    typically video blob (or non blob) objects
    """

class IGlobalConfig(Interface):
    """Interface of the annotation adapter
    """
    developer_key = TextLine(title=u'Youtube developer key')
    client_id = TextLine(title=u'Youtube client Id')

class ILocalConfig(Interface):
    auth_token = TextLine(title=u'Youtube session authsub token')
    job = TextLine(title=u'the upload job')
    youtube_link = TextLine(title=u'the youtube link')



class IYoutube(Interface):
    """Interface of the Youtube features
    """

    service = Attribute(u"the youtube gdata service")
    globalconfig = Attribute(u"the global youtube config object")
    localconfig = Attribute(u"the contextual youtube config object")

    def is_authenticated():
        """are we authenticated?
        """

    def authenticate(request):
        """authenticate given the request. We should use a GET token
        """

    def get_auth_link(request):
        """retrieve the auth link from youtube gdata service
        """

    def upload():
        """upload data. This method should return a zc.async job
        """

    def get_video():
        """return a path or a filelike object
        """





