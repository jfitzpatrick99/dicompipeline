"""
Tests for loading the dataset.
"""
from os import listdir
from dicompipeline.challenge.load_dataset import load_dataset


def test_can_load_dataset(data_dir):
  images, i_contours = load_dataset(data_dir, None)

  assert len(images) == 5, "wrong number of images loaded"
  assert len(i_contours) == 5, "wrong number of inner contour masks loaded"


def test_load_dataset_writes_intermediate_data_to_idir(data_dir, tmpdir):
  images, i_contours = load_dataset(data_dir, str(tmpdir))

  files = listdir(str(tmpdir))
  assert len(files) == 10, "wrong number of intermediate files generated"

