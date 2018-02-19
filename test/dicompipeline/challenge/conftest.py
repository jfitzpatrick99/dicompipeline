"""
Shared test fixtures.
"""
from os import path
from pytest import fixture


@fixture
def data_dir(request):
  return path.join(str(request.config.rootdir),
                   "test",
                   "fixtures",
                   "test_dataset")

