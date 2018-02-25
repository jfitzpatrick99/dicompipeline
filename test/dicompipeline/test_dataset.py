"""Tests for the Dataset class."""
from os import listdir
from dicompipeline.dataset import Dataset


def test_can_load_dataset(dicom_dir, contourfiles_dir, links_filename):
  dataset = Dataset.load_dataset(dicom_dir, contourfiles_dir, links_filename)

  assert dataset.size() == 5, "wrong number of samples loaded"

