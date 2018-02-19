"""
Tests for main entry point.
"""
from pkg_resources import load_entry_point, get_entry_info
from pytest import raises, fixture
from pprint import pprint


# TODO: pytest capsys test fixture is not working so tests are missing
# assertions to check output.


@fixture
def dicompipeline():
  return load_entry_point("dicompipeline",
    "console_scripts",
    "dicompipeline")


def test_pipeline_main_basic_invocation(dicompipeline, data_dir):
  excinfo = raises(SystemExit,
    lambda: dicompipeline(argv=["dicompipeline", "--data-dir", data_dir]))

  return_code = excinfo.value.args[0]

  assert return_code == 0, "non-zero return code for basic invocation"


def test_pipeline_main_invocation_with_idir(dicompipeline, data_dir, tmpdir):
  excinfo = raises(SystemExit,
    lambda: dicompipeline(argv=["dicompipeline",
                                "--idir", str(tmpdir),
                                "--data-dir", data_dir]))

  return_code = excinfo.value.args[0]

  assert return_code == 0, "non-zero return code for invocation with idir"


def test_pipeline_main_non_existent_data_dir(dicompipeline):
  excinfo = raises(SystemExit,
    lambda: dicompipeline(argv=["dicompipeline", "--data-dir", "foo"]))

  return_code = excinfo.value.args[0]

  assert return_code == 1, "wrong return code for non-existent data dir"


def test_pipeline_main_non_existent_idir(dicompipeline, data_dir):
  excinfo = raises(SystemExit,
    lambda: dicompipeline(argv=["dicompipeline",
                                "--idir", "foo",
                                "--data-dir", data_dir]))

  return_code = excinfo.value.args[0]

  assert return_code == 1, "wrong return code for non-existent idir"
