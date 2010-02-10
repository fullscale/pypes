class ConstExceptions:
    """
    Const exception namespace
    """
    
    class ConstError(FusionException):
        """
        Base Const exception class
        """
        _msg = None

        def __init__(self):
            if self._msg is None:
                self._msg = 'ConstError Exception: No Valid Message Defined For This Exception'
            else:
                self._msg += '\nException Class: Const Exception'
            FusionException.__init__(self, self._msg, who)
     
    class SetAttrError(ConstError):
        """
        Exception class used to handle assigment (re-binding) attempts on read-only attributes
        """

        def __init__(self, name):
            """
            @param name: The read-only attribute name that caused the exception
            @type name: String
            """
            self._msg = "Can't assign to constant variable (%s)" % name
            ConstExceptions.ConstError.__init__(self, 'SetAttrError')
    
    class DelAttrError(ConstError):
        """
        Exception class used to handle deletion attempts on read-only attribute
        """

        def __init__(self, name):
            """
            @param name: The read-only attribute name that caused the exception
            @type name: String
            """
            self._msg = "Can't unbind constant variable (%s)" % name
            ConstExceptions.ConstError.__init__(self, 'DelAttrError')

class _const:
    """
    Object for creating a constant namespace
    """

    def __setattr__(self, attr, value):
        """
        Overloaded access method that prevents re-binding of attributes in this
        namespace. This causes every attribute in the object to become constant.

        Any attribute name can be created but after creation it becomes constant.
        It cannot be changed.
        
        @param attr: Attribute attempting to be changed
        @param value: Value trying to be asign to this attribute
        """
        if self.__dict__.has_key(attr):
            raise ConstExceptions.SetAttrError, attr
        self.__dict__[attr] = value
      
    def __delattr__(self, attr):
        """
        Overloaded access method that prevents deletion of attributes in this
        namespace. Once an attribute is created in this namespace, tt cannot be deleted.

        @param attr: Attribute trying to be deleted 
        """
        if attr in self.__dict__:
            raise ConstExceptions.DelAttrError, attr
        raise NameError, attr
