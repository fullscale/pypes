=============================
 DESCRPTION 
=============================

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
J. Paul Morrison's Book titled Flow-Based Programming.

 - http://jpaulmorrison.com/fbp/

=============================
 REQUIREMENTS 
=============================

Pypes requires Stackless Python 2.6.x

You can obtain packages (both binary & source) from:

 - http://zope.stackless.com/download/sdocument_view

=============================
 INSTALLATION 
=============================

Pypes is pure python. Run python setup.py install to install the egg into your
site-packages directory. Then simply import the pypes module:

    import pypes

=============================
 USAGE
=============================

Check out the examples directory. Pypes comes with a few simple components that
are used in the included examples. These examples should provide enough insight
to get you started.

For more detailed help and/or tutorials please visit http://www.pypes.org
