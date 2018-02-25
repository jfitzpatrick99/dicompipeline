"""Tests for the model training pipeline."""
from os import listdir
from dicompipeline.dataset import Dataset
from dicompipeline.pipeline import Pipeline


def test_can_run_pipeline(dicom_dir, contourfiles_dir, links_filename):
  dataset = Dataset.load_dataset(dicom_dir, contourfiles_dir, links_filename)
  pipeline = Pipeline(dataset)

  pipeline.train()

