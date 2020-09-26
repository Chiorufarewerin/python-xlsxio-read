import os
import sys
from glob import glob
from setuptools import setup, Extension


class lazy_cythonize(list):
    def __init__(self, callback):
        self._list, self.callback = None, callback

    def c_list(self):
        if self._list is None:
            self._list = self.callback()
        return self._list

    def __iter__(self):
        for e in self.c_list():
            yield e

    def __getitem__(self, ii):
        return self.c_list()[ii]

    def __len__(self):
        return len(self.c_list())


def get_file_data(*paths) -> str:
    file_path = os.path.join(os.path.dirname(__name__), *paths)
    with open(file_path, encoding='utf-8') as f:
        return f.read()


def get_long_description() -> str:
    return get_file_data('README.md')


def get_version() -> str:
    data = get_file_data('xlsxio', '__init__.py')
    for row in data.split('\n'):
        if row.startswith("__version__ = '"):
            return row[15:].strip().strip("'")
    raise ValueError('Version string not found')


def get_extensions():
    from Cython.Build import cythonize

    is_debug = '--debug' in sys.argv or True
    compiler_directives = {
        'profile': is_debug,
        'linetrace': is_debug,
    }
    define_macros = [
        ('USE_MINIZIP', '1'),
        ('NOCRYPT', '1'),
        ('NOUNCRYPT', '1'),
    ]
    if is_debug:
        define_macros.append(('CYTHON_TRACE', '1'))
        define_macros.append(('CYTHON_TRACE_NOGIL', '1'))

    if sys.platform.startswith('linux'):
        define_macros.append(('HAVE_SYSCALL_GETRANDOM', '1'))
    if sys.platform.startswith('darwin'):
        define_macros.append(('HAVE_ARC4RANDOM_BUF', '1'))

    sources = glob('xlsxio/*.pyx')
    sources += glob('deps/xlsxio/lib/*.c')
    sources += glob('deps/expat/expat/lib/*.c')
    sources += glob('deps/zlib/*.c')
    sources += glob('deps/zlib/contrib/minizip/*.c')

    for source in sources:
        if source.endswith('minizip.c'):
            sources.remove(source)

    if not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
        sources.remove('deps/zlib/contrib/minizip/iowin32.c')

    include_dirs = [
        '.',
        'deps/xlsxio/include',
        'deps/expat/expat/lib',
        'deps/zlib',
        'deps/zlib/contrib',
    ]

    return cythonize(
        Extension(
            name='xlsxio._xlsxio',
            sources=sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
        ),
        compiler_directives=compiler_directives,
        force=True,
    )


setup(
    name='python-xlsxio',
    version=get_version(),
    license='MIT',
    url='https://github.com/Chiorufarewerin/python-xlsxio',
    author='Artur Beltsov',
    author_email='artur1998g@gmail.com',
    description='Wrapper xlsxio library for python',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=[
        'xlsxio',
    ],
    python_requires='>=3.6',
    zip_safe=False,
    keywords=[
        'xlsxio',
        'python',
        'c',
        'excel',
        'read',
    ],
    test_suite="tests",
    project_urls={
        'GitHub': 'https://github.com/Chiorufarewerin/python-xlsxio',
    },
    ext_modules=lazy_cythonize(get_extensions),
    package_data={
        'xlsxio': [
            '__init__.pyi',
        ],
    },
)
