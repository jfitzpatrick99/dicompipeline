"""Setup tools setup module.
"""

from setuptools import setup, find_packages

setup(
  name="dicompipeline",
  version="0.1.0-SNAPSHOT",
  description="dicom MRI image training pipeline",
  author="John Fitzpatrick",
  packages=find_packages(exclude=["docs", "tests"]),
  install_requires=[
    "docopt",
    "numpy",
    "Pillow",
    "pydicom",
  ],
  entry_points={
    "console_scripts": [
      "dicompipeline=dicompipeline.challenge.pipeline:main"
    ]
  },
)
