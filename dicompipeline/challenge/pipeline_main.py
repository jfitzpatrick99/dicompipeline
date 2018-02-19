"""
DICOM cardiac MRI image training pipeline.

Usage:
  dicompipeline [--log <level>] [--idir <idir>] (--data-dir <data_dir>) 
  dicompipeline (-h | --help)
  dicompipeline --version

Options:
  --log <level>          Specify the log level to use, one of "info",
                         "warning", or "debug".
  --idir <dir>           Intermediate directory containing intermediate files
                         for debugging purposes. If not specified no
                         intermediate files are generated.
  --data-dir <data_dir>  Use the given data directory for the source data set.
  -h --help              Show this screen.
  --version              Show version.

Exit Codes:
  0 if no errors occurred.
  1 on user error.
  2 on an unexpected error, e.g. lack of memory, disk, bug, etc.
"""
from docopt import docopt
import logging
from dicompipeline.challenge.load_dataset import load_dataset
from dicompipeline.challenge.pipeline import run_pipeline
import sys
import os
from traceback import format_exc
from dicompipeline.challenge.version import get_version


def main(argv=None):
  arguments = docopt(__doc__,
                     version=get_version(),
                     options_first=True,
                     help=True)

  log_level = arguments["--log"]
  if log_level is None:
    log_level = "info"
  numeric_level = getattr(logging, log_level.upper(), None)
  if not isinstance(numeric_level, int):
    logging.error("Invalid log level {}".format(logLevel))
    sys.exit(1)
  logging.basicConfig(level=numeric_level)

  data_dir = arguments["--data-dir"]
  if not os.path.isdir(data_dir):
    # Note: docopt ensures that if we are here then "data_dir" is not None
    # because "--data-dir" is mandatory per the docstring.
    logging.error("The specified data directory '{}' does not exist.".format(data_dir))
    sys.exit(1)

  idir = arguments["--idir"]
  if idir is not None and not os.path.isdir(idir):
    logging.error("The specified intermediate directory '{}' does not exist.".format(idir))
    sys.exit(1)

  try:
    images, i_contour_masks = load_dataset(data_dir, idir)

    if len(images) == 0:
      logging.error("No input images and contour masks were found in the data directory.")
      logging.error("This could happen if no contour files match any of the DICOM files even if there are images and contour files in the data directory.")
      sys.exit(1)

    run_pipeline(images, i_contour_masks, idir)
  except Exception as e:
    logging.error("An unexpected error occurred.")
    logging.error(str(e))
    logging.error(format_exc())
    sys.exit(2)
