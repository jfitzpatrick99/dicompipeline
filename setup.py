"""
Setup tools setup module.
"""
from setuptools import setup, find_packages

VERSION="0.1.0-SNAPSHOT"

setup(
  name="dicompipeline",
  version=VERSION,
  description="DICOM cardiac MRI image training pipeline",
  author="John Fitzpatrick",
  packages=find_packages(exclude=["test"]),
  install_requires=[
    "attrs",
    "cycler",
    "docopt",
    "matplotlib",
    "numpy",
    "Pillow",
    "pluggy",
    "pprint",
    "py",
    "pydicom",
    "pyparsing",
    "python-dateutil",
    "pytz",
    "scikit-learn",
    "scipy",
    "six",
  ],
  tests_require=[
    "pytest",
  ],
  entry_points={
    "console_scripts": [
      "dicompipeline=dicompipeline.main:main"
    ]
  },
)
