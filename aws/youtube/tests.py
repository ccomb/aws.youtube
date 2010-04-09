import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
#from Testing import ZopeTestCase as ztc

def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        doctestunit.DocFileSuite(
            'README.txt', package='aws.youtube',
            setUp=testing.setUp, tearDown=testing.tearDown,
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

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
