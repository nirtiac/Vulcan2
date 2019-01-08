# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sys
from unittest.mock import MagicMock


sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'Vulcan'
copyright = '2019, Aifred Health'
author = 'Robert Fratila, Priyatharsan Rajasekar, Caitrin Armstrong, \
          Joseph Mehltretter'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = '1.0'


#  on_rtd is whether we are on readthedocs.org, this line of code grabbed
#  from docs.readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'numpydoc',
    'sphinx.ext.linkcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
]

numpydoc_class_members_toctree = False

intersphinx_mapping = {
    'pytorch': ('https://pytorch.org/docs/stable/', None),
    'sklearn': ('http://scikit-learn.org/stable/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# version = '0.1'
# The full version, including alpha/beta/rc tags.
# release = '0.1'
with open('../VERSION', 'r') as f:
    release = f.read().strip()
    version = release.rsplit('.', 1)[0]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**tests**']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

def setup(app):
    app.add_stylesheet('css/my_theme.css')

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'vulcandoc'


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'Vulcan', 'Vulcan Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'Vulcan', 'Vulcan Documentation',
     author, 'Vulcan', 'One line description of project.',
     'Miscellaneous'),
]

# -- GitHub source code link ----------------------------------------------

# Functionality to build github source URI, taken from sklearn.

from operator import attrgetter
import inspect
import subprocess
from functools import partial

REVISION_CMD = 'git rev-parse --short HEAD'

def _get_git_revision():
    try:
        revision = subprocess.check_output(REVISION_CMD.split()).strip()
    except (subprocess.CalledProcessError, OSError):
        print('Failed to execute git to get revision')
        return None
    return revision.decode('utf-8')


def _linkcode_resolve(domain, info, package, url_fmt, revision):
    """Determine a link to online source for a class/method/function

    This is called by sphinx.ext.linkcode

    An example with a long-untouched module that everyone has
    >>> _linkcode_resolve('py', {'module': 'tty',
    ...                          'fullname': 'setraw'},
    ...                   package='tty',
    ...                   url_fmt='http://hg.python.org/cpython/file/'
    ...                           '{revision}/Lib/{package}/{path}#L{lineno}',
    ...                   revision='xxxx')
    'http://hg.python.org/cpython/file/xxxx/Lib/tty/tty.py#L18'
    """

    if revision is None:
        return
    if domain not in ('py', 'pyx'):
        return
    if not info.get('module') or not info.get('fullname'):
        return

    class_name = info['fullname'].split('.')[0]
    if type(class_name) != str:
        # Python 2 only
        class_name = class_name.encode('utf-8')
    module = __import__(info['module'], fromlist=[class_name])
    obj = attrgetter(info['fullname'])(module)

    try:
        fn = inspect.getsourcefile(obj)
    except Exception:
        fn = None
    if not fn:
        try:
            fn = inspect.getsourcefile(sys.modules[obj.__module__])
        except Exception:
            fn = None
    if not fn:
        return

    fn = os.path.relpath(fn,
                         start=os.path.dirname(__import__(package).__file__))
    try:
        lineno = inspect.getsourcelines(obj)[1]
    except Exception:
        lineno = ''
    return url_fmt.format(revision=revision, package=package,
                          path=fn, lineno=lineno)

def project_linkcode_resolve(domain, info):
    global _linkcode_git_revision
    return _linkcode_resolve(domain, info,
            package='Vulcan',
            revision=_linkcode_git_revision,
            url_fmt='https://github.com/Aifred-Health/Vulcan'
                    'blob/{revision}/'
                    '{package}/{path}#L{lineno}')

_linkcode_git_revision = _get_git_revision()

# The following is used by sphinx.ext.linkcode to provide links to github
linkcode_resolve = project_linkcode_resolve
#
# class Mock(MagicMock):
#     @classmethod
#     def __getattr__(cls, name):
#         return MagicMock()
#
#
# MOCK_MODULES = ['numpy', 'scipy', 'matplotlib', 'scikit-learn=0.17', 'pandas',
#                 'pydash', 'tqdm', 'torch', 'torch.utils.data',
#                 'torchvision.transforms', 'sklearn.preprocessing', 'sklearn',
#                 'torch.nn', 'matplotlib.pyplot', 'torch.optim.lr_scheduler',
#                 'torch.optim', 'sklearn.metrics', 'torch.nn.functional',
#                 'sklearn.preprocessing', 'sklearn.manifold',
#                 'sklearn.decomposition', 'mpl_toolkits.axes_grid1', 'seaborn']
# sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

