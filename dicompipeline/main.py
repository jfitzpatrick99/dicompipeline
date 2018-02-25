"""DICOM cardiac MRI image training pipeline.

Usage:
  dicompipeline [--log <level>] (--data-dir <data_dir>) 
  dicompipeline (-h | --help)
  dicompipeline --version

Options:
  --log <level>          Specify the log level to use, one of "info",
                         "warning", or "debug".
                         intermediate files are generated.
  --data-dir <data_dir>  Use the given data directory for the source data set.
  -h --help              Show this screen.
  --version              Show version.

Exit Codes:
  0 if no errors occurred.
  1 on user error.
  2 on an unexpected error, e.g. lack of memory, disk, bug, etc.
"""
import asyncio
import logging
import os
import sys

from docopt import docopt
from dicompipeline.dataset import Dataset
from dicompipeline.pipeline import Pipeline
from dicompipeline.version import get_version
from traceback import format_exc


def main(argv=None):
  if argv is None:
    # When not invoked by tests or from code, get argv from how we were
    # invoked on the command-line.
    from sys import argv

  arguments = docopt(__doc__,
                     version=get_version(),
                     options_first=True,
                     help=True,
                     argv=argv[1:])

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

  try:
    dicom_dir = os.path.join(data_dir, "dicoms")
    i_contour_dir = os.path.join(data_dir, "contourfiles")
    links_filename = os.path.join(data_dir, "link.csv")

    dataset = Dataset.load_dataset(
      dicom_dir,
      i_contour_dir,
      links_filename)

    if dataset.size() == 0:
      logging.error("No input images and contour masks were found in the data directory.")
      logging.error("This could happen if no contour files match any of the DICOM files even if there are images and contour files in the data directory.")
      sys.exit(1)

    loop = asyncio.get_event_loop()
    pipeline = Pipeline(dataset, loop=loop)
    pipeline.train()

    sys.exit(0)
  except Exception as e:
    logging.error("An unexpected error occurred.")
    logging.error(str(e))
    logging.error(format_exc())
    sys.exit(2)
