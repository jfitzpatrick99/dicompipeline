"""
Tests for the model training pipeline.
"""
from os import path, listdir
from pytest import fixture
from dicompipeline.challenge.pipeline import run_pipeline
from dicompipeline.challenge.load_dataset import load_dataset


@fixture
def data_dir(request):
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset")


def test_can_run_pipeline(data_dir):
  images, i_contours = load_dataset(data_dir, None)

  run_pipeline(images, i_contours, None)

