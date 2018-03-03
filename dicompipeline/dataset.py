"""Module defining a dataset class which contains functionality to load a
cardiac MRI training dataset from disk and iterate over it.
"""
import csv
import dicom
import logging
import numpy as np
import os
import PIL
from dicom.errors import InvalidDicomError
from PIL import Image, ImageDraw
from random import randint
from sklearn.utils import shuffle
from traceback import format_exc


PATIENT_ID_KEY="patient_id"

ORIGINAL_ID_KEY="original_id"

TOP_LEVEL_DICOMS_DIR="dicoms"

TOP_LEVEL_INNER_CONTOURS_DIR="i-contours"

CONTOUR_FILENAME_FORMAT_STR="IM-0001-{0:04d}-icontour-manual.txt"


class Dataset:
  """Dataset represents a DICOM cardiac MRI dataset"""

  def __init__(self, tuples):
    """Initialize the dataset with the given array of tuples where each tuple
    has two entries, the first being the DICOM filename for the tuple and
    the second being the file containing the inner contours for the
    corresponding DICOM file.

    :param tuples: 2-tuples for the dataset.
    :return: Dataset instance.
    """
    self._tuples = tuples
    self._size = len(tuples)


  def __iter__(self):
    """Return an iterator over the dataset."""
    # Take a copy of the tuples so that it is possible to iterate through the
    # list of tuples multiple times. This is because the list is modified in
    # place to keep track of which tuples have been processed already.
    return DatasetIter(list(self._tuples))


  def size(self):
    """Get the number of samples in the dataset."""
    return self._size


  async def batches(self, batch_size=8):
    """Asynchronous generator function that returns randomized batches of data
    in the dataset.
    """

    batch = []
    for next_tuple in self:
      batch.append(next_tuple)
      if len(batch) == batch_size:
        yield batch
        batch = []
    if len(batch) > 0:
      yield batch
    return


  @staticmethod
  def load_dataset(dicom_dir, i_contour_dir, links_filename):
    """
    Load the dataset from disk and return a dataset instance.

    :param dicom_dir: directory containing the dicom images.
    :param i_contour_dir: directory containing the inner contour data.
    :param links_filename: csv file linking dicom data to contour data.
    :return: Dataset instance.
    """

    tuples = []

    with open(links_filename, "r") as links_file:
      links_reader = csv.DictReader(links_file)

      for row in links_reader:
        # Links csv file has format patient_id,original_id where the first row
        # specifies the keys.
        patient_id = row[PATIENT_ID_KEY]
        original_id = row[ORIGINAL_ID_KEY]

        dicom_files_dir = os.path.join(dicom_dir, patient_id)
        i_contour_files_dir = os.path.join(i_contour_dir, original_id)

        logging.debug("Processing DICOM files in directory '{}' linked to contour files in directory '{}'".format(dicom_files_dir, i_contour_files_dir))

        dicom_filenames = os.listdir(dicom_files_dir)

        # Note: os.listdir returns relative file names.
        for rel_dicom_filename in dicom_filenames:
          dicom_filename = os.path.join(dicom_files_dir, rel_dicom_filename)

          # Get absolute filename for DICOM file.
          path_and_ext = os.path.splitext(rel_dicom_filename)

          if len(path_and_ext) != 2 or path_and_ext[1].upper() != ".DCM":
            logging.debug("Unexpected file with name '{}' found in DICOM data directory.".format(dicom_filename))
            continue

          instance_number = parse_int(path_and_ext[0])

          if instance_number is not None:
            dicom_filename = os.path.join(dicom_files_dir, rel_dicom_filename)
            i_contour_filename = os.path.join(i_contour_files_dir,
              TOP_LEVEL_INNER_CONTOURS_DIR,
              CONTOUR_FILENAME_FORMAT_STR.format(instance_number))

            # Only select DICOM files have corresponding contour files.
            if os.path.isfile(i_contour_filename):
              tuples.append((dicom_filename, i_contour_filename))
            else:
              logging.debug("No contour file for DICOM file '{}'".format(dicom_filename))
          else:
            logging.debug("DICOM file '{}' does not start with a valid integer.".format(dicom_filename))

    dataset = Dataset(tuples)

    return dataset


class DatasetIter:
  """Dataset iterator implementation."""

  def __init__(self, tuples, randomized=True):
    """Create an iterator instance that will iterate over the tuples in the
    dataset.

    :param tuples: List of tuples to iterate over.
    :return: Dataset iterator instance.
    """

    self._tuples = tuples
    self._randomized = randomized


  def __iter__(self):
    return self


  def __next__(self):
    """Return the next tuple in the dataset."""

    next_sample = None

    while next_sample is None:
      if len(self._tuples) > 0:
        if self._randomized:
          n = randint(0, len(self._tuples))
          next_tuple = self._tuples.pop(n)
        else:
          next_tuple = self._tuples.pop()

        dicom_filename = None
        i_contour_filename = None

        try:
          dicom_filename = next_tuple[0]
          i_contour_filename = next_tuple[1]

          dicom_dataset = parse_dicom_file(dicom_filename)
          if dicom_dataset is not None:
            pixel_data = pixel_data_for_dataset(dicom_dataset)
            width = len(pixel_data[0])
            height = len(pixel_data)
            i_contour_coords = parse_contour_file(i_contour_filename)
            i_contour_mask = poly_to_mask(i_contour_coords, width, height)

            next_sample = (pixel_data, i_contour_mask)
          else:
            logging.warning("The DICOM file '{}' is invalid.".format(dicom_filename))
        except Exception as e:
          logging.warning("An error occurred loading DICOM file '{}' and contour file '{}'.".format(dicom_filename, i_contour_filename))
          logging.warning(str(e))
          logging.warning(format_exc())
      else:
        raise StopIteration()

    return next_sample


def parse_int(s):
  """Parse the given string as an integer.
  :param s: string to parse as an integer.
  :return: Integer if the string was a valid integer or None otherwise.
  """
  try:
    return int(s)
  except ValueError:
    return None


def parse_contour_file(filename):
  """Parse the given contour filename

  :param filename: filepath to the contourfile to parse
  :return: list of tuples holding x, y coordinates of the contour
  """

  coords_lst = []

  with open(filename, 'r') as infile:
    for line in infile:
      coords = line.strip().split()

      x_coord = float(coords[0])
      y_coord = float(coords[1])
      coords_lst.append((x_coord, y_coord))

  return coords_lst


def parse_dicom_file(filename):
  """Parse the given DICOM filename

  :param filename: filepath to the DICOM file to parse
  :return: dictionary with DICOM image data
  """

  try:
    dcm = dicom.read_file(filename)
    return dcm
  except InvalidDicomError:
    return None


def poly_to_mask(polygon, width, height):
  """Convert polygon to mask

  :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
  in units of pixels
  :param width: scalar image width
  :param height: scalar image height
  :return: Boolean mask of shape (height, width)
  """

  # http://stackoverflow.com/a/3732128/1410871
  img = Image.new(mode='L', size=(width, height), color=0)
  ImageDraw.Draw(img).polygon(xy=polygon, outline=0, fill=1)
  mask = np.array(img).astype(bool)
  return mask


def pixel_data_for_dataset(dataset):
  """Get a numpy array representing the image for the given DICOM dataset
  object.

  :param dataset: DICOM dataset to get the pixel data for.
  :return: numpy array for the DICOM dataset.
  """
  intercept = 0.0
  if "RescaleIntercept" in dataset:
    intercept = dataset.RescaleIntercept

  slope = 0.0
  if "RescaleSlope" in dataset:
    slope = dataset.RescaleSlope 

  pixel_array = dataset.pixel_array
  if intercept != 0.0 and slope != 0.0:
    pixel_array = image*slope + intercept

  return pixel_array


def pil_image_for_dataset(dataset, pixel_data):
  """Generate a pillow image for the given DICOM dataset.

  Note: This function is largely a direct copy of a function from the pydicom
  library. See the pydicom file 'contrib/pydicom_PIL.py'.

  :param dataset: DICOM dataset to generate the for.
  :param pixel_data: numpy array representing the image for the dicom
  dataset.
  :return: pillow image and corresponding numpy pixel data for the image
  """
  im = None

  # can only apply LUT if these values exist
  if ('WindowWidth' not in dataset) or ('WindowCenter' not in dataset):
    bits = dataset.BitsAllocated
    samples = dataset.SamplesPerPixel
    if bits == 8 and samples == 1:
      mode = "L"
    elif bits == 8 and samples == 3:
      mode = "RGB"
    elif bits == 16:
      # not sure about this -- PIL source says is 'experimental' and no
      # documentation. Also, should bytes swap depending on endian of file and
      # system??
      mode = "I;16"
    else:
      raise TypeError("Don't know PIL mode for %d BitsAllocated and %d SamplesPerPixel" % (bits, samples))

    # PIL size = (width, height)
    size = (dataset.Columns, dataset.Rows)

    # Recommended to specify all details by
    # http://www.pythonware.com/library/pil/handbook/image.htm
    im = PIL.Image.frombuffer(mode, size, pixel_data, "raw", mode, 0, 1)
  else:
    image = get_LUT_value(pixel_data, dataset.WindowWidth, dataset.WindowCenter)
    # Convert mode to L since LUT has only 256 values:
    # http://www.pythonware.com/library/pil/handbook/image.htm
    im = PIL.Image.fromarray(image).convert('L')

  return im


def get_LUT_value(data, window, level):
  """Helper function to get lookup-up table.

  This function is a direct copy from the pydicom library. See
  'contrib/pydicom_PIL.py'.
  """
  return np.piecewise(data,
                      [data <= (level - 0.5 - (window - 1) / 2),
                       data > (level - 0.5 + (window - 1) / 2)],
                      [0, 255, lambda data: ((data - (level - 0.5)) / (window - 1) + 0.5) * (255 - 0)])

