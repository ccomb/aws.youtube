import unittest
import doctest
import os.path
from zope.testing import doctestunit
from zope.component import testing
#from Testing import ZopeTestCase as ztc
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')

def test_suite():
    suite = [
        # Unit tests for your API
        FunctionalDocFileSuite(
            'README.txt',
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),


        #doctestunit.DocTestSuite(
        #    module='aws.youtube.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use ZopeTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='aws.youtube',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='aws.youtube'),

        ]

    for s in suite:
        s.layer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

    return unittest.TestSuite(suite)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
