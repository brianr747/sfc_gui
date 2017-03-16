# coding=utf-8
"""

Based on http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
"""
import sys


if sys.version_info[0] >= 3 and sys.version_info[1] >=5:
    import importlib.util

    def loader(module_name, fpath):
        spec = importlib.util.spec_from_file_location(module_name, fpath)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo
elif sys.version_info[0] >=3 and sys.version_info[1] >=3:
    from importlib.machinery import SourceFileLoader

    def loader(module_name, fpath):
        foo = SourceFileLoader(module_name, fpath).load_module()
        return foo
else:
    import imp

    def loader(module_name, fpath):
        foo = imp.load_source(module_name, fpath)
        return foo
