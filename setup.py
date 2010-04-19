from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='aws.youtube',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Christophe Combelles',
      author_email='christophe.combelles@alterway.fr',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['aws'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.component',
          'zc.async',
          'zope.annotation',
          'zope.app.component',
          'zope.app.folder',
          'zope.contentprovider',
          'z3c.form',
          'gdata',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
