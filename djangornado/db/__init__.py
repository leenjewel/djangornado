# -*- coding:utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle

class PropertyProxy(object):
    
    def __init__(self, *args, **kwargs):
        self.property_name = kwargs.get("name")
        self.default_value = kwargs.get("default")
        self.is_primary_key = kwargs.get("primary", False)

    def set_property_name(self, name):
        if self.property_name is None:
            self.property_name = name
        return
    
    def get_property_name(self):
        return "_" + self.property_name
    
    def get_property_value(self, obj):
        if hasattr(obj, self.get_property_name()) is True:
            return getattr(obj, self.get_property_name())
        return self.default_value
    
    def set_property_value(self, obj, value):
        setattr(obj, self.get_property_name(), value)
    
    def __get__(self, obj, cla = None):
        if obj is None:
            return self
        return self.get_property_value(obj)
    
    def __set__(self, obj, value):
        self.set_property_value(obj, value)
        return


class NumberProperty(PropertyProxy):
    
    def __init__(self, *args, **kwargs):
        super(NumberProperty, self).__init__(*args, **kwargs)


class StringProperty(PropertyProxy):
    
    def __init__(self, *args, **kwargs):
        super(StringProperty, self).__init__(*args, **kwargs)


class BlobProperty(PropertyProxy):
    
    def __init__(self, *args,  **kwargs):
        super(BlobProperty, self).__init__(*args, **kwargs)


class DatetimeProperty(PropertyProxy):
    
    def __init__(self, *args, **kwargs):
        super(DatetimeProperty, self).__init__(*args, **kwargs)


def _initModel(cls, name, base, dct):
    cls._properties = []
    cls._pickle_properties = []
    cls._primary_key = None
    for property_name, property_value in dct.items():
        if isinstance(property_value, PropertyProxy):
            property_value.set_property_name(property_name)
            if property_value.is_primary_key is True:
                cls._primary_key = property_name
            cls._properties.append(property_name)
            if isinstance(property_value, BlobProperty):
                cls._pickle_properties.append(property_name)
    return


class ModelMeta(type):
    
    def __init__(cls, name, base, dct):
        super(ModelMeta, cls).__init__(name, base, dct)
        _initModel(cls, name, base, dct)

class Model(object):
    
    __metaclass__ = ModelMeta
    
    def __init__(self):
        self._is_saved = False
    
    def dump(self, properties = None, use_pickle = False, property_pickle = False):
        result_dict = {}
        if properties is None:
            properties = self._properties
        for property_name in properties:
            value = getattr(self, property_name)
            if value and property_pickle and property_name in self._pickle_properties:
                value = pickle.dumps(value, -1)
            result_dict[property_name] = value
        if use_pickle:
            return pickle.dumps(result_dict, -1)
        return result_dict
    
    @classmethod
    def load(cls, load_dict, property_pickle = False):
        if isinstance(load_dict, basestring):
            load_dict = pickle.loads(load_dict)
        result_obj = cls()
        for property_name, property_value in load_dict.items():
            if property_pickle and property_value and property_name in cls._pickle_properties:
                property_value = pickle.loads(property_value)
            setattr(result_obj, property_name, property_value)
        return result_obj
        