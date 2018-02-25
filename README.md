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

`dicompipeline --data-dir path/to/data`

Running Tests
-------------

To run the testsuite simply type `pytest` in the main project directory.

Code Layout
-----------

The top-level dicompipeline directory contains the source code for the
solution.
The top-level test directory contains tests for the solution.

Solution Overview and Rationale
-------------------------------

This section describes the design of the code and provides rationale and
justification for each of the design decisions.

The code is largely split into two parts:

* Module that provides functionality for working with the dataset
* Module that implements the training pipeline

Rationale: By separating the code into two classes, one that deals with loading
the dataset and one that deals with the training pipeline, the code will be
more maintainable and extensible because there is well defined API between the
dataset and pipeline. In particular, with this approach the pipeline class does
not need to be concerned with details about where the dataset came, the data
format and how the data is loaded.

## Dataset Module

The dataset module consists of the following:

* Dataset class used to represent the dataset
* Separate dataset iterator class which implements an iterator over the dataset
* Module level helper methods used to help loading the dataset

Rationale for separating dataset class from the iterator implementation:
The dataset class is separate from the iterator implementation because each
class addresses fundamentally separate concerns: the dataset class
is responsible for providing functionality which operators on the entire
dataset and therefore maintains state for the entire datasset while the
iterator class is responsible for maintaing state for an iteration over the
dataset. In particular there are going to be many iterations for a single
instance of the dataset.

Rationale for scanning the files that form the dataset in a static function
as opposed to an instance function or the constructor:
Doing this work in the constructor is certainly an option although in my
experience this is sub-optimal because it conveys poor semantics and violates
the principle of least surprise in the sense that it might be surprising that
calling the constructor of a class triggers a long running operation. Another
approach would be to pass in the parameters, e.g. data directories, into the
constructor and then define an instance method called "load_dataset". I dislike
this approach because it separates the code paths between where the parameters
are passed in and where they are consumed. To see why this is a problem
consider what happens if due to a bug one of the required parameters is empty:
if no checks are done in the constructor then the resulting explosion happens
in a different stack frame from where the variable was set which means the
developer now needs to figure out which call-site initialized the object with
the buggy data. Of course a solution here would be to ensure that parameters
used during dataset initialization are correct but then this introduces
maintenance overhead in the case where the valid values for a given parameter
change. In summary, using a static class method here gives:

* Clear semantics
* Clear dataflow
* Tight coupling between the parameters and the code that consumes the parameters

Rationale for using module level dataset helper functions:
The reader of the code will note that the helper functions are not Dataset
instance methods and nor are they Dataset static methods. I chose not to make
these functions instance methods because this results in poor semantics.
Specifically this would convey to readers of the code that these functions
operate on the state of the Dataset class which is not the case. Furthermore,
I chose not to make these functions static methods on the Dataset class mainly
because doing this would pollute each of the call sites with "Dataset.method"
which I think is a bit less readable. In another language such as Java where
static class methods can be called without always having to scope the function
to the class then it would certainly make much more sense to use static methods
here. The final reason why these functions are defined at the module level and
not static or instance level is that it makes refactoring them elsewhere much
more straight forward if that is needed. In fact, in my experience code that
defines instance level methods on a class where these methods don't operate
on class state makes these functions much harder to refactor later, mainly
if other developers modify them to look at class state where there is no need
to.


## Pipeline Module

The pipeline module is where the batches of the data produced by the dataset
class are processed.

This module implements both the producer and consumer coroutines used to
process the data. I chose to do this because having this code in the same place
makes the code more readable and maintainable. Of course an alternative would
have been to implement one side of the coroutine in the dataset class (or
module) but I preferred to have the queue data-structure used for this purpose
in one place.

The Pipeline class contructor takes the dataset as parameter as well as the
event loop and maximum number of batches to load into memory at once. The
dataset parameter is needed for obvious reasons, the event loop is injected
to facilitate unit testing and possibly using an alternative event loop for
advanced used cases. The parameter to specify the maximum number of batches
to load into memory at once is there to tune program memory usage. The idea
is that to trade memory for speed this value can be set higher.


Part 1: DICOM and Contour File Parsing
--------------------------------------

## How did you verify that you are parsing the contours correctly?

In order to verify that the dicom files and contour files are being parsed
correctly, the program can be invoked with a "--idir path/to/debug/dir"
argument which dumps both the original MRI scans and a modified file where the
contour line is drawn on top of the corresponding MRI scan. Example files are
shown below:

![alt text](example_images/SCD0000101-SC-HF-I-1-0048-image.png "Example original image")
![alt text](example_images/SCD0000101-SC-HF-I-1-0048-image_with_i_contour.png "Example image with inner contour line")

## What changes did you make to the functions that we provided, if any, in order to integrate them into the production code base?

I modified the "parse_dicom_file" file function to not do the slope and
intercept rescaling so that I could parse dicom files independently of having
this done. The provided parsing functions were also moved into my "dataset"
module.

## If the pipeline was going to be run on millions of images, and speed was paramount, how would you parallelize it to run as fast as possible?

I would modify the dataset loading pipeline so that rather than loading the
data in the directories inside the link.csv file serially, I would do this in
parallel. To get even more parallelism it would be possible to also divide the
files corresponding to each row of the "link.csv" file into batches and load
each of those batches in parallel.

Note about the GIL (Global Interpreter Lock):

Due to the "GIL" (Global Interpreter Lock) in python the parallelism here may
need to be implemented via separate OS processes. That said, using separate
OS processes may not result in a huge speed-up if the data loading process is
IO bound due to a slow disk for example. If separate OS processes were used,
this could be implemented using the python "multiprocessing" module.

## If this pipeline were parallelized, what kinds of error checking and/or safeguards, if any, would you add into the pipeline?

I would add safeguards to make sure that the process (or thread) used to load
each chunk of data succeeded, and if a chunk failed I would have a facility in
place that could report back which files in each chunk failed.

For debugging purposes I would make sure that failed files/chunks did not
derail the loading of successful ones. In addition I would ensure that
appropriate errors are generated for data that could not be loaded to aid
with debugging. Further to this I would consider adding functionality so that
the user could specify which files should be skipped or even to keep going even
if one or more files could not be loaded. For large, messy datasets this would
be a requirement.

Part 2: Model Training Pipeline
-------------------------------

## How did you choose to load each batch of data asynchronously, and why did you choose that method? Were there other methods that you considered - what are the pros/cons of each?

I chose to load each batch of data asynchronously using coroutines and the
producer/consumer pattern. I chose this approach because it is very obvious
as to how it works, it is suitable for IO bound processes such as what we have
with this particular problem. I also considered using the python multiprocess
module to load the data in a completely separate OS process however in testing
I found it to be slightly slower than the coroutine approach. I suspect this
might be due to the overhead of creating a new process to load the data on
each epoch. A more sophisticated approach would be to re-use a single process
each time although this would add some additional complexity. Also in my
experience the python multiprocess module has some strange failure modes which
makes debugging challening.

Pros of coroutines:

* Simple to understand
* Easy to debug

Cons of coroutines:

* Subject to the GIL (Global Interpreter Lock)
* If loading the samples is not IO bound then might be a bottleneck

Pros of separate OS processes:

* No risk of the GIL getting in the way
* Whether loading the data is IO bound or not I would expect this to give the
best performance in both cases

Cons of separate OS processes:

* Increases complexity
* Harder to debug
* Python multiprocessing module has some weird failure modes, e.g. sending
  SIGINT to a program that uses this module has strange behaviour I have not
  been able to track down.

## What kinds of error checking and/or safeguards, if any, did you build into this part of the pipeline to prevent the pipeline from crashing when run on thousands of studies?

The code that loads the individual samples is wrapped in a generic exception
handler that logs which files could not be loaded, the exception message and
the stack trace for the exception. Also, prior to getting to this point basic
sanity checks are done to make sure that the required directories exist. While
these checks don't protect against all errors they will help find mistakes
before things go to far.

## Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in this part? If so, what? If not, is there anything that you can imagine changing in the future?

Yes, I did make some changes to the pipeline. Instead of loading all of the
data up front, the changed code scans the file system for files that should
be loaded as part of the dataset. Of course this means there must be at least
enough memory to hold the filenames for all of the files of interest in memory
at once. If there was not even enough memory for this due to the sheer number
of files I could imagine making the class implementing the dataset iterator,
(DatasetIter) more sophisticated so that it would randomly choose the next
sample by first randomly selecting a row from the link csv file, finding the
corresponding DICOM directory for that row, and then randomly selecting a file
from that directory and repeating this process until a corresponding contour
file was found. This approach would still require some kind of mechanism to
keep track of previously processed DICOM files but doing this would use less
memory than my current approach since I currently store both the paths to the
DICOM files and the contour files in memory.

## How did you verify that the pipeline was working correctly?

To verify that the pipeline was working correctly I wrote log statements to log
what it was doing and I also wrote some basic unit tests.

## Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?

Some deficiencies and/or possible improvements to my code given more time would
be:

* Improve error handling to make it more user friendly, e.g. when loading
  the dataset I would invent some application specific exceptions to trap cases
  where the dataset directory is not in the expected format.
* I would definitely add more unit tests, and write additional integration
  tests.
* Tests that test the main entry point don't validate the output at all because
  I was not able to get the pytest capsys test fixture to work; I have always
  had problems with it and it would be a matter of figuring out what I did in
  the past to make it work here.
