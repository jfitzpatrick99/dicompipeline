"""Shared test fixtures."""
from os import path
from pytest import fixture


@fixture
def dicom_dir(request):
  """Return the dicom directory for the test dataset."""
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset",
                   "dicoms")


@fixture
def contourfiles_dir(request):
  """Return the contour files directory for the test dataset."""
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset",
                   "contourfiles")


@fixture
def links_filename(request):
  """Return the links filename for the test dataset."""
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset",
                   "link.csv")


@fixture
def data_dir(request):
  """Return the data directory for the test dataset."""
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset")

