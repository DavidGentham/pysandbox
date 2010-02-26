from types import FunctionType, FrameType
from sys import version_info
try:
    from sys import _clear_type_cache
except ImportError:
    # Python < 2.6 has no type cache, so we don't have to clear it
    def _clear_type_cache():
        pass

from .cpython import dictionary_of
from .restorable_dict import RestorableDict

builtin_function = type(len)

class HideAttributes:
    """
    Hide unsafe frame attributes from the Python space:
     * frame.xxx
     * function.xxx
    """
    def __init__(self):
        self.dict_dict = RestorableDict(dictionary_of(dict))
        self.function_dict = RestorableDict(dictionary_of(FunctionType))
        self.frame_dict = RestorableDict(dictionary_of(FrameType))
        self.type_dict = RestorableDict(dictionary_of(type))
        self.builtin_func_dict = RestorableDict(dictionary_of(builtin_function))

    def enable(self, sandbox):
        # Blacklist dict.__setitem__() to protect ReadOnlyBuiltins
        # FIXME: Use a cleaner fix?
        del self.dict_dict['__setitem__']
        if version_info < (3, 0):
            del self.function_dict['func_closure']
            del self.function_dict['func_globals']
        if version_info >= (2, 6):
            del self.function_dict['__closure__']
            del self.function_dict['__globals__']
        del self.frame_dict['f_locals']
        del self.type_dict['__subclasses__']
        del self.builtin_func_dict['__self__']

    def disable(self, sandbox):
        self.dict_dict.restore()
        self.function_dict.restore()
        self.frame_dict.restore()
        self.type_dict.restore()
        self.builtin_func_dict.restore()
        # Python 2.6+ uses a method cache: clear it to avoid errors
        _clear_type_cache()

