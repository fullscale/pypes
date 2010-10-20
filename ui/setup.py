try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'pypesvds',
    version = '1.1.0',
    description = 'Pypes Visual Design Studio',
    long_description = """
The pypes Visual Design Studio is a WSGI application that provides an HTTP 
service layer around the pypes component framework. It provides a REST API
that allows users to submit content from remote sources to be processed by
the framework.

Visual Design Studio also provides a complete Web 2.0 interface that allows
users to create flow based applications from any standards compliant web 
browser.

VDS also provides Paste templates for creating new components. Users can 
develop custom components that can easily be added to UI.

For detailed information regarding Flow-Based Programming concepts please see
J. Paul Morrison's Book titled `Flow-Based Programming`_.

.. _Flow-Based Programming: http://jpaulmorrison.com/fbp/

Features
--------
- Multi-Processor Support
- Micro-Thread Architecture
- Component Based
- Cross Platform
- Open Source
- Web 2.0 Interface
- REST Compliant
- Basic Authentication
- WSGI

Requirements
------------
- Stackless Python 2.6.x
- Pypes
- Paste
- Pylons >= 0.9.7
- AuthKit

Notes
-----
This a very scalable application. We're currently using it to feed over
4 million documents to Solr/Lucene. It handles all the data processing
that occurs prior to indexing. It was designed with throughput in mind
and scales up and out very easily.

Screenshots
-----------
`Visual Design Studio`_

.. _Visual Design Studio: https://sourceforge.net/project/screenshots.php?group_id=271766

Install
-------
We recommend visiting the project page and grabbing the source buildout
for this. Installing this package will pull in over 20 depencies which
will liter up your site-packages. The buildout package will isolate the
dependencies into a virtual environment and it comes with an installer.

Usage
-----
We're currently working on putting together extensive documentation
including tutorials and examples. Please watch the project home page 
for updates. 

Changelog
---------
0.1.0b2 - Released August 22, 2009
-----------------------------------
- Updated to use pypes-0.1.0b2
- Refactored components to use pypes recvall()
- Added CSV adapter/publisher component

0.1.0b1 - Released August 13, 2009
-----------------------------------
- Initial release

""",
    download_url = 'https://sourceforge.net/projects/pypes/files/',
    author = 'Eric Gaumer',
    author_email = 'egaumer@pypes.org',
    url = 'http://www.pypes.org',
    install_requires = [
        "Pylons>=0.9.7",
        "pypes",
        "py_dom_xpath",
        "authkit",
        "PasteScript>=1.6.3"
    ],
    packages = find_packages(exclude=['ez_setup']),
    include_package_data = True,
    test_suite = 'nose.collector',
    package_data = {'pypesvds': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe = False,
    paster_plugins = ['PasteScript', 'Pylons'],
    classifiers = [
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 2.6',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Framework :: Pylons',
        'Framework :: Paste',
        'Framework :: Buildout',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
    ],
    entry_points = """
        [paste.app_factory]
        main = pypesvds.config.middleware:make_app

        [paste.app_install]
        main = pylons.util:PylonsInstaller

        [paste.paster_create_template]
        studio_plugin = pypesvds.component.studioplugin:StudioPlugin

        [distutils.setup_keywords]
        paster_plugins = setuptools.dist:assert_string_list
  
        [egg_info.writers]
        paster_plugins.txt = setuptools.command.egg_info:write_arg
    """,
)
