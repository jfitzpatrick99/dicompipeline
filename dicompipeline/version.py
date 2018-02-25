"""
Utility function to get the program version number.
"""
from pkg_resources import require


__version__ = require("dicompipeline")[0].version


def get_version():
  """
  Get the program version number.
  """
  return __version__
