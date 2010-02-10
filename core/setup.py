from setuptools import setup, find_packages

setup(
  name="pypes",
  version = '0.1.0b2',
  description = 'A Flow-Based programming framework',
  long_description = """
Pypes provides a framework for building component oriented architectures. It
falls under the paradigm of Flow-Based Programming in which applications are 
defined as networks of "black box" processes, which exchange data across 
predefined connections called ports. These black box processes can be 
reconnected endlessly to form different applications without having to be 
changed internally. The concept is very similar, if not identical, to that of
Unix pipes.

Pypes is designed to build applications in a more data centric manner where
data flow is more prominent than control flow.

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
- Web 2.0 Interface (see Pypes `Visual Design Studio`_)

.. _Visual Design Studio: http://pypi.python.org/pypi/pypesvds

Requirements
------------
- Stackless Python 2.6.x

Usage
-----
We're currently working on putting together extensive documentation
including tutorials and examples. Please watch the project home page 
for updates.

Changelog
---------
0.1.0b2 - Released August 15, 2009
-----------------------------------
- Added recvall() which returns an interator over the port buffer
- Added api-docs
- Added examples

0.1.0b1 - Released August 10, 2009
-----------------------------------
- Initial release

""",
  download_url = 'https://sourceforge.net/projects/pypes/files/',
  author = 'Eric Gaumer',
  author_email = 'egaumer@pypes.org',
  url = 'http://www.pypes.org',
  classifiers = [
    'Topic :: Text Processing :: Filters',
    'Topic :: Text Processing :: Indexing',
    'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Programming Language :: Python :: 2.6',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Intended Audience :: Developers',
    'Framework :: Pylons',
    'Framework :: Paste',
    'Framework :: Buildout',
    'Environment :: Web Environment',
    'Development Status :: 4 - Beta',
  ],
  packages=["pypes"],
)

