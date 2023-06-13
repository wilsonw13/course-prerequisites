# Copyright (c) 2010-2017 Bo Lin
# Copyright (c) 2010-2017 Yanhong Annie Liu
# Copyright (c) 2010-2017 Stony Brook University
# Copyright (c) 2010-2017 The Research Foundation of SUNY
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import os.path

import _imp
from importlib import machinery
from importlib import util
# XXX: these are Python internal stuff that may very likely break in future
# releases, but is current as of 3.7:
from importlib._bootstrap import _call_with_frames_removed
from importlib._bootstrap import _verbose_message
from importlib._bootstrap_external import _get_supported_file_loaders
from importlib._bootstrap_external import _classify_pyc
from importlib._bootstrap_external import _compile_bytecode
from importlib._bootstrap_external import _validate_hash_pyc
from importlib._bootstrap_external import _validate_timestamp_pyc
from importlib._bootstrap_external import _code_to_hash_pyc
from importlib._bootstrap_external import _code_to_timestamp_pyc

# XXX: any use of `get_runtime_option` in this module must always provide a
# 'default' argument since GlobalOptions may not have been initialized yet:
from .. import common

DISTALGO_SUFFIXES = ['.da']

def da_cache_from_source(source_path, optimization=None):
    """Given the path to a .da file, return the path to its .pyc file.

    This function modifies the filename generated by importlib's
    `cache_from_source` to include the DistAlgo version number.

    """
    bytecode_path = util.cache_from_source(source_path, optimization=optimization)
    bytecode_dir, bytecode_file = os.path.split(bytecode_path)
    components = bytecode_file.split('.')
    components.insert(-1, 'da-{}'.format(common.__version__))
    bytecode_file = '.'.join(components)
    return os.path.join(bytecode_dir, bytecode_file)


class DASourceFileLoader(machinery.SourceFileLoader):
    """A source loader that loads '.da' files.

    We rely on the parent class to do most of the heavy lifting, the only places
    where we need to hook into is `source_to_code`, which is called from
    `get_code` to load the bytecode for the given source file, and
    `exec_module`, which allows us to maintain a list of all loaded DistAlgo
    modules.

    """

    def __init__(self, fullname, path):
        """This is called from the finder.

        """
        super().__init__(fullname, path)

    def exec_module(self, module):
        """Execute the module."""
        super().exec_module(module)
        # Once we get here, we can be sure that the module has been successfully
        # loaded into the system, so we register it in our system:
        common.add_da_module(module)

    def source_to_code(self, data, path, *, _optimize=-1):
        """Return the Python code object compiled from DistAlgo source.

        """
        from .. import compiler
        codeobj = _call_with_frames_removed(compiler.dastr_to_pycode,
                            data, path, _optimize=_optimize,
                            args=common.get_runtime_option(
                                'compiler_args',
                                default=[]))
        if codeobj is None:
            raise ImportError("Unable to compile {}.".format(path))
        return codeobj

    # XXX: copied wholesale from `machinery.SourceLoader`! All we really need is
    # simply alter the `bytecode_path` returned by `cache_from_source` to
    # include the DistAlgo version number:
    def get_code(self, fullname):
        """Concrete implementation of InspectLoader.get_code.

        Reading of bytecode requires path_stats to be implemented. To write
        bytecode, set_data must also be implemented.

        """
        source_path = self.get_filename(fullname)
        source_mtime = None
        source_bytes = None
        source_hash = None
        hash_based = False
        check_source = True
        try:
            # XXX: begin our change
            bytecode_path = da_cache_from_source(source_path)
            # XXX: end our change
        except NotImplementedError:
            bytecode_path = None
        else:
            # XXX: begin our change
            if not common.get_runtime_option('recompile', default=False):
                # XXX: end our change
                try:
                    st = self.path_stats(source_path)
                except OSError:
                    pass
                else:
                    source_mtime = int(st['mtime'])
                    try:
                        data = self.get_data(bytecode_path)
                    except OSError:
                        pass
                    else:
                        exc_details = {
                            'name': fullname,
                            'path': bytecode_path,
                        }
                        try:
                            flags = _classify_pyc(data, fullname, exc_details)
                            bytes_data = memoryview(data)[16:]
                            hash_based = flags & 0b1 != 0
                            if hash_based:
                                check_source = flags & 0b10 != 0
                                if (_imp.check_hash_based_pycs != 'never' and
                                    (check_source or
                                     _imp.check_hash_based_pycs == 'always')):
                                    source_bytes = self.get_data(source_path)
                                    source_hash = _imp.source_hash(
                                        _RAW_MAGIC_NUMBER,
                                        source_bytes,
                                    )
                                    _validate_hash_pyc(data, source_hash, fullname,
                                                       exc_details)
                            else:
                                _validate_timestamp_pyc(
                                    data,
                                    source_mtime,
                                    st['size'],
                                    fullname,
                                    exc_details,
                                )
                        except (ImportError, EOFError):
                            pass
                        else:
                            _verbose_message('{} matches {}', bytecode_path,
                                                        source_path)
                            return _compile_bytecode(bytes_data, name=fullname,
                                                     bytecode_path=bytecode_path,
                                                     source_path=source_path)
        if source_bytes is None:
            source_bytes = self.get_data(source_path)
        code_object = self.source_to_code(source_bytes, source_path)
        _verbose_message('code object from {}', source_path)
        if (not sys.dont_write_bytecode and bytecode_path is not None and
                source_mtime is not None):
            if hash_based:
                if source_hash is None:
                    source_hash = _imp.source_hash(source_bytes)
                data = _code_to_hash_pyc(code_object, source_hash, check_source)
            else:
                data = _code_to_timestamp_pyc(code_object, source_mtime,
                                              len(source_bytes))
            try:
                self._cache_bytecode(source_path, bytecode_path, data)
                _verbose_message('wrote {!r}', bytecode_path)
            except NotImplementedError:
                pass
        return code_object

def _install():
    """Hooks our loader into the import machinery.

    """
    da_loader = [(DASourceFileLoader, DISTALGO_SUFFIXES)]
    python_loaders = _get_supported_file_loaders()
    # Append Python's own loaders after ours, so that '.da' files are preferred
    # over same-named '.py' files:
    loaders = da_loader + python_loaders
    # make sure we are in front of the default FileFinder:
    sys.path_hooks.insert(1, machinery.FileFinder.path_hook(*loaders))
