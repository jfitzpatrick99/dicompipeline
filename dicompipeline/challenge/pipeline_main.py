"""
DICOM cardiac MRI image training pipeline.

Usage:
  dicompipeline [--idir <idir>] [--log <level>] (--data-dir <data_dir>) 
  dicompipeline (-h | --help)
  dicompipeline --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --data-dir <data_dir>  Use the given data directory for the source data set.
  --idir <dir>           Intermediate directory containing intermediate files
                         for debugging purposes.
  --log <level>          Specify the log level to use, one of "info",
                         "warning", or "debug".

Exit Codes:
  0 if no errors occurred.
  1 on user error.
  2 on an unexpected error, e.g. lack of memory, disk, etc.
"""
from docopt import docopt
import logging
from dicompipeline.challenge.load_dataset import load_dataset
from dicompipeline.challenge.pipeline import run_pipeline
import sys


def main(argv=None):
  arguments = docopt(__doc__,
                     version="0.1.0-SNAPSHOT",
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
  idir = arguments["--idir"]

  images, i_contour_masks = load_dataset(data_dir, idir)
  run_pipeline(images, i_contour_masks, idir)

