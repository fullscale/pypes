"""Provides abstract document object that represents the unit
of data both produced and consumed by components. Each 
componnet operates on a document object (or sequence of objects).
"""

import copy
import pprint
import logging
import unittest

from collections import defaultdict

LOG = logging.getLogger(__name__)

class Packet(object):
    """Represents the unit of information passed between components within the 
    data flow graph.
    """

    def __init__(self, doc=None, meta=None, attr_meta=None):
        """Constructor
        
        @param doc: attributes to use
        @type doc: dictionary, default None
        @param meta: packet metadata to use
        @type meta: dictionary, default None
        @param attr_meta: attribute metadata to use
        @type attr_meta: dictionary, default None
        """
        if doc is None:
            doc = {}
        else:
            doc = copy.deepcopy(doc)
        
        if meta is None:
            meta = {}
        else:
            meta = copy.deepcopy(meta)
        
        if attr_meta is None:
            attr_meta = {}
        else:
            attr_meta = copy.deepcopy(attr_meta)
            
        self._doc = defaultdict(list, doc)
        self._meta = meta
        self._attr_meta = defaultdict(dict, attr_meta)

    def pprint(self, meta=False):
        """Prints the document object

        @param meta: if metadata should be printed or not
        @type meta: boolean, default False
        """
        sorted_fields = [(k, self._doc[k]) for k in sorted(self._doc.keys())]
        printer = pprint.PrettyPrinter(indent=4)
        print 'Attributes:'
        printer.pprint(sorted_fields)
        
        if meta:
            sorted_meta = [(k, self._meta[k]) \
                            for k in sorted(self._meta.keys())]
            sorted_attr_meta = [(k, self._attr_meta[k]) \
                                    for k in sorted(self._attr_meta.keys())]
            print 'Packet Meta'
            printer.pprint(sorted_meta)
            print 'Attribute Meta'
            printer.pprint(sorted_attr_meta)

    def get(self, attr, default=None):
        """Returns the attribute or the default value if it does not exist.

        @param attr: the attribute to get
        @type attr: string
        @param default:  the default value to return
        @type default: any, default None
        @return: string if single value, list if multivalue, default if the
            attribute does not exist.
        """

        if attr in self._doc:
            value = self._doc[attr]
            if len(value) == 1:
                value = value[0]
            else:
                value = value[:]
        else:
            value = default
            
        return value

    def set(self, attr, value, multi=False, keep_meta=True):
        """Sets the attribute, overwriting any existing value(s).  If multi 
        is True and value is a list, the attribute will be set to multivalued 
        and each item in value will be a value for the attribute.  If meta is 
        false, all metadata for the attribute will be lost.

        @param attr: the attribute to set
        @type attr: string
        @param value: the value to assign to the attribute
        @type value: any
        @param multi: if value should be treated as multivalued
        @type multi: boolean, default False
        @param keep_meta: if related metadata should be deleted or not
        @type keep_meta: boolean, default True
        """
            
        if isinstance(value, list) and multi:
            self._doc[attr] = value[:]
        else:
            self._doc[attr] = [value]
            
        if not keep_meta and attr in self._attr_meta:
            del self._attr_meta[attr]

    def add(self, attr, value, multi=False):
        """Sets the attribute only if it does not already exist.  If multi is 
        True and value is a list, then the attribute will be set multivalued and
        each item in value will be a value for the attribute.

        @param attr: the attribute to add
        @type attr: string
        @param value: the value to assign the attribute
        @type value: any
        @param multi: If value should be treated as multiple values
        @type multi: boolean, default False
        """
        
        if attr in self._doc:
            LOG.debug('Attribute %s exists, not adding!' % attr)
        else:
            self.set(attr, value, multi, False)

    def append(self, attr, value, extend=False):
        """Appends a value to an attribute. If the attribute is not already
        multivalued then it becomes multivaliued.  If extend is True and value
        is a list, then each item in value becomes a value in the attribute.

        @param attr: the attribute to append to
        @type attr: string
        @param value: the value to append to the attribute
        @type value: any
        @param extend: if we extend the existing items
        @type extend: boolean, default False
        """
        
        if isinstance(value, list) and extend:
            self._doc[attr].extend(value)
        else:
            self._doc[attr].append(value)
                    
    def delete(self, attr):
        """Delete an attribute.  All metadata related to the attribute will be 
        lost.

        @param attr: the attribute to delete
        @type attr: string
        @return: True if success, False if failed
        """
        success = False
        try:
            del self._doc[attr]
            if attr in self._attr_meta:
                del self._attr_meta[attr]

            success = True
        except KeyError:
            pass       
        
        return success

    def remove(self, attr, index=0):
        """Remove an item from the attribute.  If the attribute is not 
        multivalued, this is equilavent to a delete.  If the attribute is 
        multivalued, the item at the specified index will be removed.

        @param attr: the attribute to remove an item from
        @type attr: string
        @param index: the index of the item to remove
        @type index: integer (0 = first item), default 0
        @return: True if success, False if failed
        """
        success = False
        try:
            # try to remove the item, if it results in
            # an empty attribute, delete the attribute altogether
            del self._doc[attr][index]
            if not self._doc[attr]:
                self.delete(attr)
                
            success = True
        except (IndexError, KeyError):
            pass
        
        return success

    def replace(self, attr, value, index=0):
        """Replaces an item in the attribute.  If the attribute is not
        multivalued, this is equilavent to a set.  If the attribute is
        multivalued, the item at the specified index will be replaced.
        The index position must already exist, or the call will fail.

        @param attr: the attribute to replace an item from
        @type attr: string
        @param value: the replacement value
        @type value: any
        @param index: the index of the item to replace
        @type index: integer (0 = first item), default 0
        @return: True if success, False if failed
        """
        success = False
        try:
            self._doc[attr][index] = value
            success = True
        except (IndexError, KeyError):
            pass
        
        return success

    def has(self, attr):
        """Returns true if the document has the attribute, false otherwise.

        @param attr: the attribute to check for
        @type attr: string 
        @return: True if the attribute exists, False otherwise
        """
        
        return self._doc.has_key(attr)

    def get_attributes(self):
        """Returns the document as a dictionary.

        @return: the attributes as a dictionary
        """
        
        return copy.deepcopy(dict(self._doc))

    def get_attribute_names(self):
        """Returns the names of the document attributes as a list.

        @return: the attribute names as a list
        """
        return sorted(self._doc.keys())

    def get_metas(self):
        """Returns tuple of metadata.  The first item is the packet metadata as 
        a dictionary and the second item is the attribtue metadata as a 
        dictionary.

        @return: tuple, (packet meta, attribute meta)
        """
        
        return (copy.deepcopy(self._meta), copy.deepcopy(dict(self._attr_meta)))
    
    def get_meta_names(self):
        """Returns tuple of metadata names.  The first item is the packet 
        metadata names as a list and the second item is the attribtue metadata 
        names in a dictionary with the attribute name as the key, and a list as
        the value.

        @return: tuple, (packet meta, attribute meta)
        """
        
        attr_names = {}
        for attr in self._attr_meta:
            attr_names[attr] = sorted(self._attr_meta[attr].keys())
            
        return (sorted(self._meta.keys()), attr_names)
            
    def set_meta(self, meta, value, attr=None):
        """Set a metadata value.  If the metadata value already exists, it will
        be overwritten.  To set metadata on an attribute, supply the optional
        attr parameter.  This method will return False if the supplied attribute
        does not exist.

        @param meta: the meta key
        @type meta: string
        @param value: the meta value
        @type value: any 
        @param attr: the attribute to set metadata for
        @type attr: string, default None
        @return: True of success, False otherwise.
        """
        
        success = False
        if attr is None:
            self._meta[meta] = value
            success = True
        elif attr in self._doc:
            self._attr_meta[attr][meta] = value
            success = True
        
        return success

    def get_meta(self, meta, attr=None, default=None):
        """Return the metadata value if it exists, otherwise the default value 
        is returned.

        @param meta: the meta key
        @type meta: string 
        @param attr: the attribute to get metadata from
        @type attr: string, default None
        @param default: the default value if meta does not exist
        @type default: any, default None
        @return: metadata value if exists, otherwise the default value
        """
        
        if attr is None and meta in self._meta:
            value = self._meta[meta]
        elif attr in self._attr_meta and meta in self._attr_meta[attr]:
            value = self._attr_meta[attr][meta]
        else:
            value = default
            
        return value

    def delete_meta(self, meta, attr=None):
        """Deletes a metadata value. 

        @param meta: the meta key
        @type meta: string 
        @param attr: the attribute to delete metadata from
        @type attr: string, default None
        @return: True on success, False otherwise
        """

        success = False
        try:
            if attr is None:
                del self._meta[meta]
                success = True
            elif attr in self._attr_meta:
                del self._attr_meta[attr][meta]
                success = True
        except KeyError:
            pass

        return success
        
    def has_meta(self, meta, attr=None):
        """Checks if a given metadata value exists.

        @param meta: the meta key to check for
        @type meta: string 
        @param attr: the attribute to check for the metadata
        @type attr: string, default None
        @return: True if meta exists, False otherwise
        """
        
        if attr is None:
            has_meta = meta in self._meta
        else:
            has_meta = meta in self._attr_meta[attr]
            
        return has_meta

    def is_multivalued(self, attr):
        """Returns True if the attribute is multivalued.

        @param attr: the attribute to check is multivalued
        @type attr: string  
        @return: True if the attribute is multivalued, False otherwise
        """
        
        is_multi = False
        if attr in self._doc:
            is_multi = (len(self._doc[attr]) > 1)
            
        return is_multi

    def clone(self, metas=True):
        """Creates a copy of the document. If metas is True then meta 
        information is also copied.

        @param metas: If we include metadata in the clone
        @type metas: boolean, default True 
        @return: Copy of the L{Packet} object
        """
        if metas:
            meta = self._meta
            attr_meta = dict(self._attr_meta)
        else:
            meta = {}
            attr_meta = {} 
        
        return Packet(self._doc, meta, attr_meta)

    def merge(self, other, metas=False):
        """Merges this document with another document. If metas is False, meta 
        information is not merged.

        @param other: the other document to be merged
        @type other: L{Packet} object
        @param metas: True merges meta information
        @type metas: boolean, default False 
        """
        
        if metas:
            meta, attr_meta = other.get_metas()
            self._meta.update(meta)
            self._attr_meta.update(attr_meta)
            
        self._doc.update(other.get_attributes())

    def __iter__(self):
        """Packet iterator

        @return: tuple (key/value) pairs
        """
        sorted_fields = [(k, self._doc[k]) for k in sorted(self._doc.keys())]
        for field in sorted_fields:
            yield field

    def __eq__(self, rhs):
        """Packet == operator

        @param rhs: The other packet to compare
        @type rhs: L{Packet} object 
        """
        
        try:
            r_meta, r_attr_meta = rhs.get_metas()
            r_doc = rhs.get_attributes()
            result = (self._doc == r_doc) and \
                     (self._meta == r_meta) and \
                     (self._attr_meta == r_attr_meta)
        except AttributeError:
            result = False

        return result

    def __ne__(self, rhs):
        """Packet != operator

        @param rhs: the L{Packet} on the right hand side of the operator
        @type rhs: L{Packet} object
        """

        return (not self == rhs)


class PacketUnitTest(unittest.TestCase):
    """Unit test for L{Packet}"""
    
    def setUp(self):
        """Default test setup"""
        self.doc = Packet()
        
    def test_get(self):
        """Test get"""
        self.doc.set('a', 1)
        self.assertEqual(self.doc.get('a'), 1, 'Failed get')
        self.assertEqual(self.doc.get('b'), None, 'Failed get')
        self.assertEqual(self.doc.get('b', 'default'), 'default', 'Failed get')

    def test_set(self):
        """Test set""" 
        # if we can set an attribute that does not exist
        self.doc.set('a', 1)
        self.assertEqual(self.doc.get('a'), 1, 'Failed set')
        
        # if we can overwrite an attribute that already exists
        self.doc.set('a', 2)
        self.assertEqual(self.doc.get('a'), 2, 'Failed set')
        
        # if we can set a list as a value to an attribute
        self.doc.set('a', [1, 2])
        self.assertEqual(self.doc.is_multivalued('a'), False, 'Failed set')
        
        # if we can set a list a multivalued attribute
        self.doc.set('a', [1, 2], multi=True)
        self.assertEqual(self.doc.is_multivalued('a'), True, 'Failed set')
        
        # if we can keep metadata on sets
        # verify value has been changed and metadata is still attached
        self.doc.set_meta('meta1', 'test', 'a')
        self.doc.set('a', 1)
        self.assertEqual(self.doc.has_meta('meta1', 'a'), True, 'Failed set')
        self.assertEqual(self.doc.get('a'), 1, 'Failed set')
        
        # if we can purge metadata on sets
        # verify value has been changed and metadata does not exist.
        self.doc.set('a', 2, keep_meta=False)
        self.assertEqual(self.doc.has_meta('meta1', 'a'), False, 'Failed set')
        self.assertEqual(self.doc.get('a'), 2, 'Failed set')
    
    def test_add(self):
        """Test add"""
        # if we can add an attribute
        self.doc.add('a', 1)
        self.assertEqual(self.doc.get('a'), 1, 'Failed add')
        
        # if we don't overwrite existing attribute
        self.doc.add('a', 2)
        self.assertNotEqual(self.doc.get('a'), 2, 'Failed add')
        
    def test_append(self):
        """Test append"""
        # append a single value to non-existing attribute
        self.doc.append('a', 1)
        self.assertEqual(self.doc.get('a'), 1, 'Failed append')
        
        # append to existing attribute
        self.doc.append('a', 2)
        self.assertEqual(self.doc.get('a'), [1, 2], 'Failed append')
        
        # append a list as a single item
        self.doc.append('a', [3, 4])
        self.assertEqual(self.doc.get('a'), [1, 2, [3, 4]], 'Failed append')
        
        # append a list as multiple items (extending)
        self.doc.append('a', [5, 6], extend=True)
        self.assertEqual(self.doc.get('a'), 
            [1, 2, [3, 4], 5, 6], 'Failed append')
        
    def test_delete(self):
        """Test delete"""
        # delete non-existing item
        self.assertEqual(self.doc.delete('a'), False, 'Failed delete')
        
        # delete item without meta
        self.doc.set('a', 1)
        self.assertEqual(self.doc.delete('a'), True, 'Failed delete')
        self.assertEqual(self.doc.has('a'), False, 'Failed delete')
        
        # delete item with meta
        self.doc.set('a', 2)
        self.doc.set_meta('meta1', 'test', 'a')
        self.assertEqual(self.doc.delete('a'), True, 'Failed delete')
        self.assertEqual(self.doc.has('a'), False, 'Failed delete')
        self.assertEqual(self.doc.has_meta('meta1', 'a'), False, 
            'Failed delete')
        
    def test_remove(self):
        """Test remove"""
        # remove non-existing attribute
        self.assertEqual(self.doc.remove('a'), False, 'Failed remove')
        
        # remove single item attribute
        self.doc.set('a', 1)
        self.assertEqual(self.doc.remove('a'), True, 'Failed remove')
        self.assertEqual(self.doc.has('a'), False, 'Failed remove')
        
        # remove item from multi-valued attribute
        self.doc.set('a', [1, 2, 3], multi=True)
        self.assertEqual(self.doc.remove('a'), True, 'Failed remove')
        self.assertEqual(self.doc.get('a'), [2, 3], 'Failed remove')
        
        # remove non-zero index
        self.assertEqual(self.doc.remove('a', 1), True, 'Failed remove')
        self.assertEqual(self.doc.get('a'), 2, 'Failed remove')
        
        # remove non-existing index
        self.assertEqual(self.doc.remove('a', 10), False, 'Failed remove')
        self.assertEqual(self.doc.get('a'), 2, 'Failed remove')
        
    def test_has(self):
        """Test has"""
        # non-existing attribute
        self.assertEqual(self.doc.has('a'), False, 'Failed has')
        
        # existing item
        self.doc.set('a', 1)
        self.assertEqual(self.doc.has('a'), True, 'Failed has')
        
    def test_get_attributes(self):
        """Test get_attributes"""
        # empty packet
        self.assertEqual(self.doc.get_attributes(), 
            {}, 'Failed get_attributes')
        
        # single item packet
        self.doc.set('a', 1)
        self.assertEqual(self.doc.get_attributes(), 
            {'a': [1]}, 'Failed get_attributes')
        
        # multiple item packet
        self.doc.set('b', 2)
        self.assertEqual(self.doc.get_attributes(), {'a': [1], 'b': [2]}, 
            'Failed get_attributes')
        
        # packet with multivalued item
        self.doc.set('c', [3, 4])
        self.assertEqual(self.doc.get_attributes(), 
            {'a': [1],'b': [2],'c':[[3,4]]}, 'Failed get_attributes')
        
    def test_get_attribute_names(self):
        """Test get_attribute_names"""
        # empty packet
        self.assertEqual(self.doc.get_attribute_names(), [], 
            'Failed get_attribute_names')
        
        # single item packet
        self.doc.set('a', 1)
        self.assertEqual(self.doc.get_attribute_names(), ['a'], 
            'Failed get_attribute_names')
        
        # multi item packet
        self.doc.set('z', 1)
        self.assertEqual(self.doc.get_attribute_names(), ['a', 'z'],
            'Failed get_attribute_names')
        
        # multi item sorted
        self.doc.set('m', 1)
        self.doc.set('c', 1)
        self.doc.set('w', 1)
        self.assertEqual(self.doc.get_attribute_names(), 
            ['a', 'c', 'm', 'w', 'z'], 'Failed get_attribute_names')
        
    def test_get_metas(self):
        """Test get_metas"""
        # empty packet
        self.assertEqual(self.doc.get_metas(), ({}, {}), 'Failed get_metas')
        
        # single packet meta
        self.doc.set_meta('pm1', 1)
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1}, {}), 
            'Failed get_metas')
        
        # single packet meta and single attribute meta
        self.doc.set('a', 1)
        self.doc.set_meta('am1', 1, 'a')
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1}, {'a': {'am1': 1}}), 
            'Failed get_metas')
        
        # single packet meta, multi attribute meta
        self.doc.set('b', 2)
        self.doc.set_meta('am2', 2, 'b')
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1}, 
            {'a': {'am1': 1}, 'b': {'am2': 2}}), 'Failed get_metas')
        
        # multi packet meta, multi attribute meta
        self.doc.set_meta('pm2', 2)
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1, 'pm2': 2}, 
            {'a': {'am1': 1}, 'b': {'am2': 2}}), 'Failed get_metas')
        
        # single attribute meta
        self.doc.delete('b')
        self.doc.delete_meta('pm2')
        self.doc.delete_meta('pm1')
        self.assertEqual(self.doc.get_metas(), ({}, {'a': {'am1': 1}}), 
            'Failed get_metas')
        
    def test_get_meta_names(self):
        """Test get_meta_names"""
        # empty packet
        self.assertEqual(self.doc.get_meta_names(), ([], {}), 
            'Failed get_meta_names')
        
        # single packet meta
        self.doc.set_meta('pm1', 1)
        self.assertEqual(self.doc.get_meta_names(), (['pm1'], {}), 
            'Failed get_meta_names')
        
        # single packet meta and single attribute meta
        self.doc.set('a', 1)
        self.doc.set_meta('am1', 1, 'a')
        self.assertEqual(self.doc.get_meta_names(), (['pm1'], {'a': ['am1']}), 
            'Failed get_meta_names')
        
        # single packet meta, multi attribute meta
        self.doc.set('b', 2)
        self.doc.set_meta('am2', 2, 'b')
        self.assertEqual(self.doc.get_meta_names(), (['pm1'], {'a': ['am1'], 
            'b': ['am2']}), 'Failed get_meta_names')
        
        # multi packet meta, multi attribute meta
        self.doc.set_meta('pm2', 2)
        self.assertEqual(self.doc.get_meta_names(), (['pm1', 'pm2'], 
            {'a': ['am1'], 'b': ['am2']}), 'Failed get_meta_names')
        
        # multi packet meta, multi attribute meta and multiple attribute meta
        self.doc.set_meta('am3', 3, 'b')
        self.assertEqual(self.doc.get_meta_names(), (['pm1', 'pm2'], 
            {'a': ['am1'], 'b': ['am2', 'am3']}), 'Failed get_meta_names')
        
        # single attribute meta
        self.doc.delete('b')
        self.doc.delete_meta('pm2')
        self.doc.delete_meta('pm1')
        self.assertEqual(self.doc.get_meta_names(), ([], {'a': ['am1']}), 
            'Failed get_meta_names')
        
    def test_set_meta(self):
        """Test set_meta"""
        # packet meta
        self.assertEqual(self.doc.set_meta('pm1', 1), True, 'Failed set_meta')
        self.assertEqual(self.doc.get_meta('pm1'), 1, 'Failed set_meta')
        
        # override packet meta
        self.assertEqual(self.doc.set_meta('pm1', 2), True, 'Failed set_meta')
        self.assertEqual(self.doc.get_meta('pm1'), 2, 'Failed set_meta')
        
        # attribute meta on missing attribute
        self.assertEqual(self.doc.set_meta('am1', 1, 'a'), False, 
            'Failed set_meta')
        
        # attribute meta
        self.doc.set('a', 1)
        self.assertEqual(self.doc.set_meta('am1', 1, 'a'), True, 
            'Failed set_meta')
        self.assertEqual(self.doc.get_meta('am1', 'a'), 1, 
            'Failed set_meta')
        
        # override attribute meta
        self.assertEqual(self.doc.set_meta('am1', 2, 'a'), True, 
            'Failed set_meta')
        self.assertEqual(self.doc.get_meta('am1', 'a'), 2, 
            'Failed set_meta')
        
    def test_get_meta(self):
        """Test get_meta"""
        # empty packet meta
        self.assertEqual(self.doc.get_meta('pm1'), None, 'Failed get_meta')
        self.assertEqual(self.doc.get_meta('pm1', default='default'), 
            'default', 'Failed get_meta')
        
        # empty attribute meta
        self.assertEqual(self.doc.get_meta('am1', 'a'), None, 'Failed get_meta')
        self.assertEqual(self.doc.get_meta('am1', 'a', 'default'), 
            'default', 'Failed get_meta')
        
        # packet meta
        self.doc.set_meta('pm1', 1)
        self.assertEqual(self.doc.get_meta('pm1'), 1, 'Failed get_meta')
        
        # attribute meta
        self.doc.set('a', 1)
        self.doc.set_meta('am1', 1, 'a')
        self.assertEqual(self.doc.get_meta('am1', 'a'), 1, 'Failed get_meta')
        
    def test_delete_meta(self):
        """Test delete_meta"""
        # empty packet
        self.assertEqual(self.doc.delete_meta('pm1'), False, 
            'Failed delete_meta')
        self.assertEqual(self.doc.delete_meta('am1', 'a'), False, 
            'Failed delete_meta')
        
        # packet meta
        self.doc.set_meta('pm1', 1)
        self.assertEqual(self.doc.delete_meta('pm1'), True, 
            'Failed delete_meta')
        self.assertEqual(self.doc.get_meta('pm1'), None, 
            'Failed delete_meta')
        
        # attribute meta
        self.doc.set('a', 1)
        self.doc.set_meta('am1', 1, 'a')
        self.assertEqual(self.doc.delete_meta('am1', 'a'), True, 
            'Failed delete_meta')
        self.assertEqual(self.doc.get_meta('am1', 'a'), None, 
            'Failed delete_meta')
        
    def test_has_meta(self):
        """Test has_meta"""
        # empty packet
        self.assertEqual(self.doc.has_meta('pm1'), False, 'Failed has_meta')
        self.assertEqual(self.doc.has_meta('am1', 'a'), False, 
            'Failed has_meta')
        
        # packet meta
        self.doc.set_meta('pm1', 1)
        self.assertEqual(self.doc.has_meta('pm1'), True, 'Failed has_meta')
        
        # attribute meta
        self.doc.set('a', 1)
        self.doc.set_meta('am1', 1, 'a')
        self.assertEqual(self.doc.has_meta('am1', 'a'), True, 'Failed has_meta')
        
    def test_is_multivalued(self):
        """Test is_multivalued"""
        # empty packet
        self.assertEqual(self.doc.is_multivalued('a'), False, 
            'Failed is_multivalued')
        
        # single value
        self.doc.set('a', 1)
        self.assertEqual(self.doc.is_multivalued('a'), False, 
            'Failed is_multivalued')
        
        # multivalued by append
        self.doc.append('a', 2)
        self.assertEqual(self.doc.is_multivalued('a'), True, 
            'Failed is_multivalued')
        
        # multivalued by assignment
        self.doc.set('b', [1, 2, 3], multi=True)
        self.assertEqual(self.doc.is_multivalued('b'), True, 
            'Failed is_multivalued')
        
    def test_clone(self):
        """Test clone"""
        # empty packet
        pp2 = self.doc.clone()
        self.assertEqual(pp2 is self.doc, False, 'Failed clone')
        self.assertEqual(pp2.get_metas(), ({}, {}), 'Failed clone')
        self.assertEqual(pp2.get_attributes(), {}, 'Failed clone')
        
        # packet with attribuets
        self.doc.set('a', 1)
        self.doc.set('b', 2)
        pp3 = self.doc.clone()
        self.assertEqual(pp3 is self.doc, False, 'Failed clone')
        self.assertEqual(pp3.get_metas(), ({}, {}), 'Failed clone')
        self.assertEqual(pp3.get_attributes(), {'a': [1], 'b': [2]}, 
            'Failed clone')
        
        # packet with attribuets and meta
        self.doc.set_meta('pm1', 1)
        self.doc.set_meta('am1', 1, 'a')
        pp4 = self.doc.clone()
        self.assertEqual(pp4 is self.doc, False, 'Failed clone')
        self.assertEqual(pp4.get_metas(), ({'pm1': 1}, {'a': {'am1': 1}}), 
            'Failed clone')
        self.assertEqual(pp4.get_attributes(), {'a': [1], 'b': [2]},
            'Failed clone')
        
    def test_merge(self):
        """Test merge"""
        # empty packet with non-empty, no metas
        pp2 = Packet()
        pp2.set('a', 1)
        pp2.set('b', 2)
        pp2.set_meta('pm1', 1)
        pp2.set_meta('am1', 1, 'a')
        self.doc.merge(pp2)
        self.assertEqual(self.doc.get_metas(), ({}, {}), 'Failed merge')
        self.assertEqual(self.doc.get_attributes(), {'a': [1], 'b': [2]}, 
            'Failed merge')
        
        # empty packet with non-empty, with metas
        self.doc = Packet()
        self.doc.merge(pp2, metas=True)
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1}, {'a': {'am1': 1}}),
            'Failed merge')
        self.assertEqual(self.doc.get_attributes(), {'a': [1], 'b': [2]},
            'Failed merge')
        
        # non-empty with non-empty
        pp2.set('c', 3)
        pp2.set('a', 4)
        pp2.set_meta('pm2', 2)
        pp2.set_meta('am2', 2, 'c')
        pp2.set_meta('am1', 3, 'a')
        self.doc.merge(pp2, metas=True)
        self.assertEqual(self.doc.get_metas(), ({'pm1': 1, 'pm2': 2}, 
            {'a': {'am1': 3}, 'c': {'am2': 2}}), 'Failed merge')
        self.assertEqual(self.doc.get_attributes(), {'a': [4], 'b': [2], 
            'c': [3]}, 'Failed merge')
        
    def test_iter_eq_ne(self):
        """Test __iter__, __eq__, and __ne__"""
        # iter
        self.doc.set('a', [1, 2, 3], multi=True)
        self.doc.set('b', [4, 5])
        self.doc.set('c', 'test')
        self.assertEqual([x for x in self.doc], [('a', [1, 2, 3]), 
            ('b', [[4, 5]]), ('c', ['test'])], 'Failed iter')
        
        # eq
        pp2 = self.doc.clone()
        pp3 = Packet()
        self.assertEqual(pp2 == self.doc, True, 'Failed eq')
        self.assertEqual(pp3 == self.doc, False, 'Failed eq')
        self.assertEqual(self.doc == 2, False, 'Failed eq')
        
        # ne
        self.assertEqual(pp2 != self.doc, False, 'Failed ne')
        self.assertEqual(pp3 != self.doc, True, 'Failed ne')
        
    def test_pprint(self):
        """Test pprint"""
        self.doc.set('a', [1, 2, 3], multi=True)
        self.doc.set('b', [[4, 5], 6], multi=True)
        self.doc.set('c', 'test')
        self.doc.set_meta('pm1', 1)
        self.doc.set_meta('am1', 1, 'a')
        
        print
        self.doc.pprint()
        print
        self.doc.pprint(meta=True)
        

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(PacketUnitTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
