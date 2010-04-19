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

    >>> t = transaction.begin()

Youtube interface and adapter
-----------------------------

The Youtube interface exposes the available features added to a video file,
while the IGlobalConfig and ILocalConfig allow to access configuration:

>>> from aws.youtube.interfaces import IYoutube, ILocalConfig, IGlobalConfig
>>> IYoutube
<InterfaceClass aws.youtube.interfaces.IYoutube>
>>> IGlobalConfig
<InterfaceClass aws.youtube.interfaces.IGlobalConfig>

To be able to retrieve an adapter or a youtube view, we have a marker interface
to tag any object with youtube capability:

>>> from aws.youtube.interfaces import IYoutubeable

Then we can create an arbitraty object and let it provide
this interface. As an example, we use an interface similar to
plone.app.blob.IATBlob:

>>> from zope.app.folder import Folder

>>> from zope.interface import classImplements
>>> classImplements(Folder, IYoutubeable)

We create an instance:

>>> mysample = Folder()

We store it in the root:

>>> root['Application']['sample'] = mysample
>>> transaction.commit()

We set an *annotatable* sitemanager on it (to be able to store config as
annotation):

>>> from zope.app.component.site import LocalSiteManager
>>> from zope.annotation.interfaces import IAttributeAnnotatable
>>> sm = LocalSiteManager(root['Application'])
>>> from zope.interface import alsoProvides
>>> alsoProvides(sm, (IAttributeAnnotatable,))
>>> root['Application'].setSiteManager(sm)

We register the SiteManagerAdapter (normally done with zcml from
zope.app.component):

>>> from zope.app.component.site import SiteManagerAdapter
>>> from zope.component import getGlobalSiteManager
>>> getGlobalSiteManager().registerAdapter(SiteManagerAdapter)


Now we have a IYoutube adapter and an annotations adapter on this object:
(we first register them)

>>> from aws.youtube.adapters import globalconfig, localconfig, TestYoutube
>>> getGlobalSiteManager().registerAdapter(globalconfig)
>>> getGlobalSiteManager().registerAdapter(localconfig)
>>> getGlobalSiteManager().registerAdapter(TestYoutube)

We also have to register the standard annotations adapter
(normally done in ZCML)

>>> from zope.annotation.attribute import AttributeAnnotations
>>> getGlobalSiteManager().registerAdapter(AttributeAnnotations)

Now we can retrieve our adapter:

>>> IGlobalConfig(mysample)
<aws.youtube.adapters.GlobalConfig object at ...>

The adapter is an annotation adapter that stores additional data.
The globalconfig is stored in the nearest sitemanager

>>> from zope.component import getSiteManager
>>> globalconfig(mysample).foobar = 'baz'
>>> print list(getSiteManager(mysample).__annotations__.items())
[('aws.youtube.adapters.GlobalConfig', <aws.youtube.adapters.GlobalConfig object at ...>)]






We can ask for a authentication link:

>>> from zope.publisher.browser import TestRequest
>>> from z3c.form.interfaces import IFormLayer
>>> import urllib2
>>> urllib2.unquote(IYoutube(mysample).get_auth_link(TestRequest()))
'https://www.google.com/accounts/AuthSubRequest?scope=http://gdata.youtube.com&session=1&secure=0&hd=default&next=http://127.0.0.1/sample?auth_sub_scopes=http%3A%2F%2Fgdata.youtube.com'

Then we can authenticate with a single-use token provided by google:

>>> single_use_token = 'ABCDEFGHIJKL'

>>> IYoutube(mysample).authenticate(TestRequest())

This will store the token so that we can use it in later requests:

>>> token = ILocalConfig(mysample).auth_token
>>> token
''

The URL was not correct, here is a good one, but this is not a real token so it
fails:

>>> tokenrequest = TestRequest(environ={'token': single_use_token,'QUERY_STRING': 'token=%s' % single_use_token,})
>>> from aws.youtube.views import Authenticate
>>> Authenticate(mysample, tokenrequest)()
Traceback (most recent call last):
...
NonAuthSubToken
>>> token = ILocalConfig(mysample).auth_token
>>> token
''



Upload content provider
-----------------------


When we are not authenticated, we only get an auth link

>>> from zope.publisher.browser import TestRequest, BrowserView
>>> from aws.youtube.views import UploadContentProvider
>>> anyrequest = TestRequest()
>>> alsoProvides(anyrequest, IFormLayer)
>>> anyview = BrowserView(mysample, anyrequest)

We call the content provider:

>>> contentprovider = UploadContentProvider(mysample, anyrequest, anyview)
>>> contentprovider.update()
>>> print contentprovider.render()
<div id="aws.youtube.upload">
    <a href="https://www.google.com/accounts/AuthSubRequest?scope=http%3A%2F%2Fgdata.youtube.com&amp;session=1&amp;secure=0&amp;hd=default&amp;next=http%3A%2F%2F127.0.0.1%2Fsample%3Fauth_sub_scopes%3Dhttp%253A%252F%252Fgdata.youtube.com">Authenticate on Youtube!</a>
</div>

Now we will use a valid session token:

>>> import os
>>> from ConfigParser import ConfigParser
>>> testconfig = os.path.join(os.path.expanduser('~'), '.aws.youtube')
>>> if not os.path.exists(testconfig):
...     print 'to run tests, please create a %s file with parameters below' % testconfig
>>> parser = ConfigParser()
>>> p = parser.read(testconfig)
>>> SESSION_TOKEN = parser.get('youtube', 'session_token')
>>> DEVELOPER_KEY = parser.get('youtube', 'developer_key')
>>> CLIENT_ID = parser.get('youtube', 'client_id')

>>> ILocalConfig(mysample).auth_token = SESSION_TOKEN
>>> mysample.__annotations__['aws.youtube.adapters.LocalConfig'].auth_token == SESSION_TOKEN
True
>>> contentprovider = UploadContentProvider(mysample, anyrequest, anyview)
>>> contentprovider.update()
>>> print contentprovider.render()
<div id="aws.youtube.upload">
    <a href="@@youtube_upload">Upload to Youtube!</a>
</div>


We need a form to configure the developer key and application id. This is
provided in another content provider:

>>> from aws.youtube import views
>>> form = views.GlobalConfig(mysample, anyrequest)
>>> form.update()
>>> print form.render()
<form action=".">
...
<input type="text" id="form-widgets-developer_key"
...
<input type="text" id="form-widgets-client_id"
...
</form>

If we submit the form, the developer key is saved:

>>> submitrequest = TestRequest(
...     form={
...         'form.widgets.developer_key': unicode(DEVELOPER_KEY),
...         'form.widgets.client_id': unicode(CLIENT_ID),
...         'form.buttons.apply': u'Apply',
...     })
>>> alsoProvides(submitrequest, IFormLayer)
>>> form = views.GlobalConfig(mysample, submitrequest)
>>> form.update()
>>> print form.render()
<i>Data successfully updated.</i>
...

The values are stored in the annotations:

>>> DEVELOPER_KEY == IGlobalConfig(mysample).developer_key
True
>>> CLIENT_ID == IGlobalConfig(mysample).client_id
True

We can use the upload view to launch the upload in background:

>>> from aws.youtube.views import Upload
>>> uploadview = Upload(mysample, anyrequest)
>>> uploadview()
>>> transaction.commit()


While the video is being uploaded, the content provider displays a status:

>>> contentprovider = UploadContentProvider(mysample, anyrequest, anyview)
>>> contentprovider.update()
>>> print contentprovider.render()
<div id="aws.youtube.upload">
    <span>The video is being uploaded to you tube!</span>
</div>

The job is stored in annotations. We wait for the job to finish:

>>> job = ILocalConfig(mysample).job
>>> zc.async.testing.wait_for_result(job, seconds=500)

Once it is uploaded, it displays the link to the youtube video, and a link to
delete it.

>>> contentprovider = UploadContentProvider(mysample, anyrequest, anyview)
>>> contentprovider.update()
>>> print contentprovider.render()
    <div id="aws.youtube.upload">
        <a href="http://www.youtube.com/watch?v=...&amp;feature=youtube_gdata">This video is on Youtube!</a>
        <a href="">Delete from youtube</a>
    </div>


clean up

    >>> zc.async.ftesting.tearDown()













