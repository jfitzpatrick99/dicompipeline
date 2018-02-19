from pkg_resources import load_entry_point, get_entry_info
from pytest import raises
from pprint import pprint

def test_pipeline_main_displays_usage_with_no_args(capsys):
  dicompipeline = load_entry_point("dicompipeline", "console_scripts", "dicompipeline")

  entry_info = get_entry_info("dicompipeline", "console_scripts", "dicompipeline")

  raises(SystemExit, lambda: dicompipeline(argv=["dicompipeline"]))

  # TODO: Work on actual assertions
