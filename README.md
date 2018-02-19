Introduction
------------

This project implements an MRI image data-processing pipeline which aims to
learn where the inner contour of the left ventricle of the heart is located
in an MRI image.

Pre-Requisites
--------------

* Python version 3 interpreter with pip
* virtualenv and virtualenvwrapper are recommended
* git (needed to clone source)

For instructions on installing python see:

https://www.python.org/downloads/

For instructions on installing virtualenvwrapper see:

http://virtualenvwrapper.readthedocs.io/en/latest/

Instructions for installing git can be found at:

https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

Installation (for development)
------------------------------

The project can be setup using the following steps:

1. mkvirtualenv dicompipeline
2. git clone https://github.com/jfitzpatrick99/dicompipeline
3. cd dicompipeline
4. pip install -e .

Running
-------

To run the pipeline, execute the following command:

dicompipeline --data-dir path/to/data

Code Layout
-----------

The top-level dicompipeline directory contains the source code for the
solution.
The top-level test directory contains tests for the solution.
