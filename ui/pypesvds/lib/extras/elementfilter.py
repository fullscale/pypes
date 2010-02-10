##################################################################################
# Copyright (c) 2006  Gerard Flanagan
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included
#    in all copies or substantial portions of the Software.
#
# Requires 'elementtree' which can be obtained from:
#
#   http://www.effbot.org/zone/element-index.htm
#
##################################################################################

import re
try:
    from xml.etree import cElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

RE_ATTRIBUTE = re.compile("(?<=@)[^\]]+$")

#RE_XPATH = re.compile("/({[^}]+})?([\w|*]+)?(?:\[(.+)\])?") 
RE_XPATH = re.compile("/({[^}]+})?([\w|*|-]+)?(?:\[(.+)\])?") 

class InvalidFilterException(Exception): pass

class MultipleResultsException(Exception): pass

def _find_elements_by_specification( element, specs):
    '''
    Recursively search subnodes of 'element' for those nodes which
    meet the specification associated with the level of recursion,
    eg. the second spec is associated with the grandchildren of 'element'.
    Returns the nodes found at the last level.
    '''
    if not specs:
        return element[:]
    else:
        nodes = (elem for elem in element[:] if specs[0].is_satisfied_by(elem))
        more_specs = specs[1:]
        if not more_specs:
            return  list(nodes)
        else:
        #search subnodes
            result = []
            for node in nodes:
                result.extend( _find_elements_by_specification(node, more_specs) )
            return result

def _remove_elements_by_specification(element, specs):
    '''
    Recursively search subnodes of 'element' for those nodes which
    meet the specification associated with the level of recursion,
    eg. the second spec is associated with the grandchildren of 'element'.
    Removes the nodes found at the last level.
    '''
    if not specs:
        return
    else:
        nodes = (elem for elem in element[:] if specs[0].is_satisfied_by(elem))
        more_specs = specs[1:]
        if not more_specs:
            for node in nodes:
                element.remove( node )
        else:
            for node in nodes:
                _remove_elements_by_specification(node, more_specs)

class _NodeSpecification(object):

    def __init__(self, namespace=None, tag=None, filter=None):
        self.ns = namespace
        self.tag = tag or '*'
        self.filter = filter

    def is_satisfied_by(self, element):
        result = False
        if self.ns:
            if self.tag == '*' and element.tag.startswith(self.ns):
                result = True
            tag = self.ns + self.tag
        else:
            tag = self.tag
        result = result or tag == '*' or tag == element.tag
        if result and self.filter:
            expr = self.filter
            for key,value in element.items():
                #print key, value
                key = '@' + key
                try:
                    float(value)
                except ValueError:
                    value = "\"%s\"" % value
                expr = expr.replace( key, value )
            try:
                return eval(expr)
            except:
                return False #raise InvalidFilterException()
        return result

def _filterpath_to_node_specification( filterpath ):
    '''
    >>> def parse_filter(path):
    ...     specs, attr =  _filterpath_to_node_specification(path)
    ...     return [(s.ns, s.tag, s.filter) for s in specs], attr
    ...
    >>> parse_filter('book[@author==Hopkins]/@barcode')
    ([('', 'book', '@author==Hopkins')], 'barcode')
    >>> parse_filter('books/*/title/author')
    ([('', 'books', ''), ('', '*', ''), ('', 'title', ''), ('', 'author', '')], None)
    >>> parse_filter('{ns}book[@price<20]/{ns}title')
    ([('{ns}', 'book', '@price<20'), ('{ns}', 'title', '')], None)
    >>> parse_filter('@id')
    ([], 'id')
    >>> parse_filter('@{ns}id')
    ([], '{ns}id')
    >>> parse_filter('{ns}@id')
    Traceback (most recent call last):
        ...
    InvalidFilterException
    >>> parse_filter('{ns}*')
    ([('{ns}', '*', '')], None)
    >>> parse_filter('{ns}*') == parse_filter('{ns}')
    True
    >>> parse_filter('{ns}/@id')
    ([('{ns}', '*', '')], 'id')
    >>> parse_filter('{ns}*[@name.startswith("A")]/@id')
    ([('{ns}', '*', '@name.startswith("A")')], 'id')
    >>> parse_filter('/portal/content-node[@create-type==explicit]/@action')
    ([('', 'portal', ''), ('', 'content-node', '@create-type==explicit')], 'action')
    '''
    specs = []
    #does the filterpath end with an attribute, eg. @id ?
    #Note: RE_ATTRIBUTE will produce id, not @id
    attr = re.search(RE_ATTRIBUTE, filterpath)
    if attr:
        attr = attr.group(0)
        #remove the attribute just found from the filterpath
        filterpath =  re.sub(RE_ATTRIBUTE, '', filterpath)
        #strip trailing @
        filterpath = filterpath[:-1]
        if filterpath and filterpath[-1] != '/': raise InvalidFilterException()
    else:
        attr = None
    if filterpath:
        #the filterpath passed to RE_XPATH.findall() must begin with a forward slash
        if filterpath[0] != '/':
            filterpath = '/' + filterpath
        #strip any trailing forward slash
        if filterpath[-1] == '/':
            filterpath = filterpath[:-1]
    for ns, tag, filter in RE_XPATH.findall(filterpath):
        specs.append( _NodeSpecification(ns, tag, filter) )
    return specs, attr 

class ElementFilter(object):

    attribute_default = None
    
    def __get_filter(self):
        return self.__filter
    
    def __set_filter(self, filter):
        self.__filter = filter
        self.specs, self.attribute  = _filterpath_to_node_specification(filter)
        self._cache = None
        self._doc = None
        self._count = None

    filter = property( __get_filter,__set_filter )       

    def __get_filtered(self):
        if self._cache is None:
            self._cache = _find_elements_by_specification( self.element, self.specs )
        return self._cache
    
    filtered = property( __get_filtered )

    def __init__(self, element, filterpath=''):
        self.element = element
        self.__set_filter( filterpath )
        
    def findall(self):
        if self.attribute is None:
            return self.filtered
        else:
            #note that the presence of a default value for a non-present key means that
            #for attributes: self.count() = len(self.data()) <= len(self.findall())
            return  [ e.get(self.attribute, self.attribute_default) for e in self.filtered ]

    def removeall(self):
        if self.attribute is None:
            _remove_elements_by_specification( self.element, self.specs )
        else:
            for elem in self.filtered:
                if self.attribute in elem.attrib:
                    del elem.attrib[self.attribute] 

    def count(self):
        if self._count is None:
            if self.attribute is None:
                self._count = len(self.filtered)
            else:
                self._count = len(self.data())
        return self._count

    def data(self):
        if self.attribute is None:
            return [ elem.text for elem in self.filtered ]
        else:
            return [ attr for attr in self.findall() if attr is not self.attribute_default ]
        
    def distinct_values(self):
        return set(self.data())
     
    def doc(self, tag="root"):
        if self._doc is None:
            root = ET.Element(tag)
            for elem in self.filtered:
                root.append(elem)
            self._doc = ET.ElementTree(root)
        return self._doc
    
    def empty(self):
        return bool(self.count())

    def replace(self, old, new, count=-1):
        for elem in self.filtered:
            if self.attribute is None:
                elem.text = elem.text.replace(old, new, count)
                elem.tail = elem.tail.replace(old, new, count)
            else:
                oldval = elem.get(self.attribute)
                if oldval:
                    elem.set(self.attribute, oldval.replace(old, new, count))

    def sub(self, pattern, repl, count=0, deep=False):
        changes = 0
        for elem in self.filtered:
            if self.attribute is None:
                newval, i = re.subn(pattern, repl, elem.text, count)
                elem.text = newval
                changes += i
                if deep:
                    for child in elem.getiterator():
                        newval, i = re.subn(pattern, repl, child.text, count)
                        child.text = newval
                        changes += i
                        newval, i = re.subn(pattern, repl, child.tail, count)
                        child.tail = newval
                        changes += i
            else:
                oldval = elem.get(self.attribute)
                newval = re.sub(pattern, repl, oldval, count)
                if newval != oldval:
                    elem.set(self.attribute, newval)
                    changes += 1
        return changes

    def zero_or_one(self):
        result = self.findall()
        if len(result) > 1:
            raise MultipleResultsException()
        return result
    
    def text(self):
        result = self.zero_or_one()
        if not result:
            return None
        if self.attribute is None:
            return result[0].text
        else:
            return result[0]

def findall( element, filterpath ):
    '''
    >>> XML1, XML2 = _testdata()
    >>> [elem.text for elem in findall(XML1, "channel/item/title")]
    ['Normalizing XML, Part 2', 'The .NET Schema Object Model', "SVG's Past and Promising Future"]
    >>> [elem.text for elem in findall(XML1, "channel/item/creator")]
    []
    >>> #NB. James Clark format for namespace-qualified elements
    >>> [elem.text for elem in findall(XML1, "channel/item/{http://purl.org/dc/elements/1.1/}creator")]
    ['Will Provost', 'Priya Lakshminarayanan', 'Antoine Quint']
    >>> findall( XML2, 'category/item[@id=="A001"]/@colour' )
    ['red']
    >>> findall( XML2, 'category/item[@id.startswith("A")]/@colour' )
    ['red', 'blue', 'yellow']
    >>> findall( XML2, 'category[@id<500]/@id' )
    ['123', '456']
    '''
    return ElementFilter( element, filterpath ).findall()

def removeall( element, filterpath ):
    '''
    >>> XML1, XML2 = _testdata()
    >>> filterpath = "channel/item/title"
    >>> [elem.text for elem in findall(XML1, filterpath)]
    ['Normalizing XML, Part 2', 'The .NET Schema Object Model', "SVG's Past and Promising Future"]
    >>> removeall(XML1, filterpath)
    >>> [elem.text for elem in findall(XML1, filterpath)]
    []
    >>> filter = ElementFilter( XML2, "category/item/@colour")
    >>> filter.findall()
    ['red', 'blue', 'yellow', 'pink', 'blue', None, 'pink', 'orange', 'blue']
    >>> filter.removeall()
    >>> filter.findall()
    [None, None, None, None, None, None, None, None, None]
    '''
    ElementFilter( element, filterpath ).removeall()

def count( element, filterpath ):
    '''
    >>> XML1, XML2 = _testdata()
    >>> count(XML1, 'channel/item')
    3
    >>> count(XML2, 'category/item[@colour=="blue"]')
    3
    '''
    return ElementFilter( element, filterpath ).count()

def data( element, filterpath ):
    '''
    >>> XML1, XML2 = _testdata()
    >>> data(XML1, "channel/item/title")
    ['Normalizing XML, Part 2', 'The .NET Schema Object Model', "SVG's Past and Promising Future"]
    >>> data(XML2, "category/item/@colour")
    ['red', 'blue', 'yellow', 'pink', 'blue', 'pink', 'orange', 'blue']
    '''
    return ElementFilter( element, filterpath ).data()

def doc( element, filterpath, tag="root" ):
    '''
    Returns an ElementTree instance whose document root is a 'tag'
    element, and whose subnodes are the elements satisfying the filterpath
    
    >>> XML1, XML2 = _testdata()
    >>> filterpath = 'category/item[@colour=="blue"]'
    >>> root = doc(XML2, filterpath).getroot()
    >>> len(root[:])
    3
    '''
    return ElementFilter(element, filterpath).doc(tag)

def replace( element, filterpath, old, new, count=-1):
    '''
    Replace strings within text elements or attributes
    
    >>> XML1, XML2 = _testdata()
    >>> filter = ElementFilter(XML1, "channel/title")
    >>> filter.data()
    ['XML.com']
    >>> filter.replace('XML', 'xml')
    >>> filter.data()
    ['xml.com']
    >>> filter = ElementFilter(XML2, "category/item/@colour")
    >>> filter.data()
    ['red', 'blue', 'yellow', 'pink', 'blue', 'pink', 'orange', 'blue']
    >>> filter.replace('pink', 'lilac')
    >>> filter.data()
    ['red', 'blue', 'yellow', 'lilac', 'blue', 'lilac', 'orange', 'blue']
    '''
    ElementFilter(element, filterpath).replace(old, new, count)

def sub(element, filterpath, pattern, repl, count=0):
    return ElementFilter(element, filterpath).sub(pattern, repl, count)

def text(element, filterpath):
    '''
    >>> XML1, XML2 = _testdata()
    >>> text(XML1, 'channel/title')
    'XML.com'
    >>> text(XML1, 'channel/item')
    Traceback (most recent call last):
       ...
    MultipleResultsException
    '''
    return ElementFilter(element, filterpath).text()

def _test():
    import doctest
    doctest.testmod()

def _testdata():
    return ET.fromstring(RSS_TEST), ET.fromstring(ATTR_TEST)

RSS_TEST = ''' <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel encoding="utf-8">
    <title>XML.com</title>
    <link>http://www.xml.com/</link>
    <description>XML.com features a rich mix of information and services for the XML community.</description>
    <language>en-us</language>
    <item>
      <title>Normalizing XML, Part 2</title>
      <link>http://www.xml.com/pub/a/2002/12/04/normalizing.html</link>
      <description>In this second and final look at applying relational normalization techniques to W3C XML Schema data modeling, Will Provost discusses when not to normalize, the scope of uniqueness and the fourth and fifth normal forms.</description>
      <dc:creator>Will Provost</dc:creator>
      <dc:date>2002-12-04</dc:date>    
    </item>
    <item>
      <title>The .NET Schema Object Model</title>
      <link>http://www.xml.com/pub/a/2002/12/04/som.html</link>
      <description>Priya Lakshminarayanan describes in detail the use of the .NET Schema Object Model for programmatic manipulation of W3C XML Schemas.</description>
      <dc:creator>Priya Lakshminarayanan</dc:creator>
      <dc:date>2002-12-04</dc:date>    
    </item>
    <item>
      <title>SVG's Past and Promising Future</title>
      <link>http://www.xml.com/pub/a/2002/12/04/svg.html</link>
      <description>In this month's SVG column, Antoine Quint looks back at SVG's journey through 2002 and looks forward to 2003.</description>
      <dc:creator>Antoine Quint</dc:creator>
      <dc:date>2002-12-04</dc:date>    
    </item>
  </channel>
</rss>'''

ATTR_TEST = '''<root>
    <title lang="en" encoding="utf-8">Document Title</title>
    <category id="123" code="A">
        <item id="A001" colour="red">Item A1</item>
        <item id="A002" colour="blue">Item A2</item>
        <item id="A003" colour="yellow">Item A3</item>
    </category>
    <category id="456" code="B">
        <item id="B001" colour="pink">Item B1</item>
        <item id="B002" colour="blue">Item B2</item>
        <item id="B003" >Item B3</item>
    </category>
    <category id="789" code="C">
        <item id="C001" colour="pink">Item C1</item>
        <item id="C002" colour="orange">Item C2</item>
        <item id="C003" colour="blue">Item C3</item>
    </category>
</root>'''

if __name__ == '__main__':
    _test()

