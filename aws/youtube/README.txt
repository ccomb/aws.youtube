aws.youtube Package Readme

We first setup zc.async to be able to do long upload or download tasks:

    >>> import transaction
    >>> import ZODB.FileStorage, ZODB.blob
    >>> from ZODB.DB import DB
    >>> import tempfile

    >>> import zc.async.configure
    >>> zc.async.configure.base()
    >>> import zc.async.queue
    >>> from zope.component import getGlobalSiteManager
    >>> getGlobalSiteManager().registerAdapter(zc.async.queue.getDefaultQueue)
    >>> blobdir = tempfile.mkdtemp()
    >>> storage = ZODB.blob.BlobStorage(blobdir, ZODB.FileStorage.FileStorage(
    ...     'zc_async.fs', create=True))
    >>> db = DB(storage)
    >>> conn = db.open()
    >>> root = conn.root()
    >>> from zope.app.folder.folder import rootFolder
    >>> PseudoZopeRoot = root['Application'] = rootFolder()
    >>> transaction.commit()
    >>> def _getRootObject():
    ...     return PseudoZopeRoot
    ...
    >>> globals()['getRootFolder'] = _getRootObject
    >>> import zc.async.ftesting
    >>> zc.async.ftesting.setUp()
    >>> transaction.commit()


Youtube interface and adapter
-----------------------------

The Youtube interface exposes the available features added to a video file:

>>> from aws.youtube.interfaces import IYoutube, IYoutubeAnnotations
>>> IYoutube
<InterfaceClass aws.youtube.interfaces.IYoutube>
>>> IYoutubeAnnotations
<InterfaceClass aws.youtube.interfaces.IYoutubeAnnotations>

To be able to retrieve an adapter or a youtube view, we have a marker interface
to tag any object with youtube capability:

>>> from aws.youtube.interfaces import IYoutubeable

Then we can create an arbitraty object and let it provide
this interface. As an example, we use an interface similar to
plone.app.blob.IATBlob:

>>> from zope.app.folder import Folder
>>> from zope.location import Location
>>> class Sample(Folder, Location):
...     title = 'some title'
...     blob = 'some data'
...     __name__ = 'sample'

>>> from zope.interface import classImplements
>>> classImplements(Sample, IYoutubeable)

We create an instance:

>>> mysample = Sample()

We store it in the root:

>>> PseudoZopeRoot['sample'] = mysample

We set an *annotatable* sitemanager on it (to be able to store config as
annotation):

>>> from zope.app.component.site import LocalSiteManager
>>> from zope.annotation.interfaces import IAttributeAnnotatable
>>> sm = LocalSiteManager(PseudoZopeRoot)
>>> from zope.interface import alsoProvides
>>> alsoProvides(sm, (IAttributeAnnotatable,))
>>> PseudoZopeRoot.setSiteManager(sm)

We register the SiteManagerAdapter (normally done with zcml from
zope.app.component):

>>> from zope.app.component.site import SiteManagerAdapter
>>> from zope.component import getGlobalSiteManager
>>> getGlobalSiteManager().registerAdapter(SiteManagerAdapter)


Now we have a IYoutube adapter and an annotations adapter on this object:
(we first register them)

>>> from aws.youtube.adapters import youtubeannotations, Youtube
>>> getGlobalSiteManager().registerAdapter(youtubeannotations)
>>> getGlobalSiteManager().registerAdapter(Youtube)

We also have to register the standard annotations adapter
(normally done in ZCML)

>>> from zope.annotation.attribute import AttributeAnnotations
>>> getGlobalSiteManager().registerAdapter(AttributeAnnotations)

Now we can retrieve our adapter:

>>> IYoutubeAnnotations(mysample)
<aws.youtube.adapters.YoutubeAnnotations object at ...>

The adapter is an annotation adapter that stores additional data:

>>> IYoutubeAnnotations(mysample).foobar = 'baz'
>>> print list(mysample.__annotations__.items())
[('aws.youtube.adapters.YoutubeAnnotations', <aws.youtube.adapters.YoutubeAnnotations object at ...>)]






We can ask for a authentication link:

>>> from zope.publisher.browser import TestRequest
>>> IYoutube(mysample).get_auth_link(TestRequest())
'https://www.google.com/accounts/AuthSubRequest?scope=http%3A%2F%2Fgdata.youtube.com&session=1&secure=0&hd=default&next=http%3A%2F%2F127.0.0.1%2Fsample%3Fauth_sub_scopes%3Dhttp%253A%252F%252Fgdata.youtube.com'

Then we can authenticate with a single-use token provided by google:

>>> single_use_token = 'ABCDEFGHIJKL'

>>> IYoutube(mysample).authenticate(TestRequest())

This will store the token so that we can use it in later requests:

>>> token = IYoutubeAnnotations(mysample).auth_token
>>> token
''

The URL was not correct, here is a good one, but this is not a real token so it
fails:

>>> IYoutube(mysample).authenticate(TestRequest(environ={'token': single_use_token, 'QUERY_STRING': 'token=%s' % single_use_token,}))
Traceback (most recent call last):
...
NonAuthSubToken
>>> token = IYoutubeAnnotations(mysample).auth_token
>>> token
''




Upload content provider
-----------------------

When we are not authenticated, we only get an auth link

>>> from aws.youtube.views import Upload
>>> from zope.publisher.browser import TestRequest, BrowserView

>>> anyrequest = TestRequest()
>>> anyview = BrowserView(mysample, anyrequest)

We call the content provider:

>>> uploadview= Upload(mysample, anyrequest, anyview)
>>> uploadview.update()
>>> print uploadview.render()
    <div id="aws.youtube.upload">
        <a href="">Authenticate to your Youtube account</a>
    </div>

If we use our stored session token, the content provider displays the upload
button:

>>> IYoutubeAnnotations(mysample).auth_token = token
>>> uploadview.update()
>>> print uploadview.render()
    <div id="aws.youtube.upload">
        <a href="@@youtube_upload">Upload to Youtube!</a>
    </div>

While the video is being uploaded, the content provider displays a status:

>>> IYoutubeAnnotations(mysample).auth_token = token
>>> uploadview.update()
>>> print uploadview.render()
    <div id="aws.youtube.upload">
        <span>The video is being uploaded to you tube!</span>
    </div>

Once it is uploaded, it displays the link to the youtube video, and a link to
delete it.

>>> IYoutubeAnnotations(mysample).auth_token = token
>>> uploadview.update()
>>> print uploadview.render()
    <div id="aws.youtube.upload">
        <a href="">This video is on Youtube!</a>
        <a href="">Delete from youtube</a>
    </div>


clean up

    >>> zc.async.ftesting.tearDown()













