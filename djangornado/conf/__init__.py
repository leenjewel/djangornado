# -*-coding:utf-8 -*-

import os
from djangornado.utils.importlib import import_module

__all__ = ['settings', 'urls']

ENVIRONMENT_VARIABLE = 'DJANGORNADO_SETTINGS_MODULE'

class LazySettings(dict):
    def __init__(self):
        try:
            settings_path = os.environ[ENVIRONMENT_VARIABLE]
            if not settings_path: # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            # NOTE: This is arguably an EnvironmentError, but that causes
            # problems with Python's interactive help.
            raise ImportError('No settings file path given, because environment variable %s is undefined.' % ENVIRONMENT_VARIABLE)
        self.settings_module = import_module(settings_path)
        self.settings_dict = self.settings_module.__dict__
        super(LazySettings, self).__init__(self.settings_dict.items())
    
    def __getattr__(self, attr):
        return self.get(attr)

settings = LazySettings()