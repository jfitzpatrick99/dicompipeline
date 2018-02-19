"""
Module containing function to load a dataset from a given data directory.
"""
import os
import csv
from dicompipeline.challenge.parsing import parse_contour_file, parse_dicom_file, poly_to_mask
import PIL
import logging
import numpy as np


PATIENT_ID_KEY="patient_id"

ORIGINAL_ID_KEY="original_id"


TOP_LEVEL_DICOMS_DIR="dicoms"

TOP_LEVEL_CONTOURS_DIR="contourfiles"

TOP_LEVEL_INNER_CONTOURS_DIR="i-contours"

CONTOUR_FILENAME_FORMAT_STR="IM-0001-{0:04d}-icontour-manual.txt"

LINK_FILENAME="link.csv"


def load_dataset(data_dir, idir):
  """Load the dataset from the given data directory and use the provided
  intermediate directory to store intermediate files for debugging purposes.

  :param data_dir: data directory to load the dataset from
  :param idir: intermediate directory to use for debugging. If set to None then
  no intermediate images are generated.
  :return: 2D array where each row contains an image and the corresponding
  contour lines for the image.
  """
  logging.info("Starting pipeline using data from data_dir " + data_dir)

  the_dataset = []

  links_filename = os.path.join(data_dir, LINK_FILENAME)
  with open(links_filename, "r") as links_file:
    links_reader = csv.DictReader(links_file)
    for row in links_reader:
      # Links csv file has format patient_id,original_id where the first row
      # specifies the keys.
      patient_id = row[PATIENT_ID_KEY]
      original_id = row[ORIGINAL_ID_KEY]

      dicom_files_dir = os.path.join(data_dir,
        TOP_LEVEL_DICOMS_DIR,
        patient_id)
      i_contour_files_dir = os.path.join(data_dir,
        TOP_LEVEL_CONTOURS_DIR,
        original_id)

      logging.info("Processing DICOM files in dir {} linked to contour files in dir {}".format(dicom_files_dir, i_contour_files_dir))

      dicom_filenames = os.listdir(dicom_files_dir)

      # Note: os.listdir returns relative file names.
      for rel_dicom_filename in dicom_filenames:
        # Get absolute filename for DICOM file.
        dicom_filename = os.path.join(dicom_files_dir, rel_dicom_filename)
        dataset = parse_dicom_file(dicom_filename)

        if dataset is not None:
          if "InstanceNumber" in dataset:
            i_contour_filename = os.path.join(i_contour_files_dir,
              TOP_LEVEL_INNER_CONTOURS_DIR,
              CONTOUR_FILENAME_FORMAT_STR.format(int(dataset.InstanceNumber)))

            # Only select DICOM files have corresponding contour files.
            if os.path.isfile(i_contour_filename):
              pil_image, pixel_data = pil_image_for_dataset(dataset)
              width = len(pixel_data[0])
              height = len(pixel_data)
              i_contour_coords = parse_contour_file(i_contour_filename)
              i_contour_mask = poly_to_mask(i_contour_coords, width, height)

              # If intermediate directory specified, write debug images.
              if idir is not None:
                pil_image_filename = os.path.join(idir,
                  "{0}-{1}-{2:04d}-image.png".format(patient_id,
                  original_id,
                  int(dataset.InstanceNumber)))
                pil_image.save(pil_image_filename)

                i_contour_image_filename = os.path.join(idir,
                  "{0}-{1}-{2:04d}-image_with_i_contour.png".format(patient_id,
                  original_id,
                  int(dataset.InstanceNumber)))
                PIL.ImageDraw.Draw(pil_image).polygon(xy=i_contour_coords,
                  outline=255)
                pil_image.save(i_contour_image_filename)

              the_dataset.append([pixel_data, i_contour_mask])
            else:
              logging.debug("No contour file for DICOM file {}".format(dicom_filename))
          else:
            logging.warning("DICOM file {} is missing InstanceNumber and/or pixel data".format(dicom_filename))
        else:
          logging.warning("DICOM file {} is invalid.".format(dicom_filename))

  return the_dataset


def pil_image_for_dataset(dataset):
  """Generate a pillow image for the given DICOM dataset.

  Note: This function is largely a direct copy of a function from the pydicom
  library. See the pydicom file 'contrib/pydicom_PIL.py'.

  :param dataset: DICOM dataset to generate the for.
  :return: pillow image and corresponding numpy pixel data for the image
  """
  im = None

  intercept = 0.0
  if "RescaleIntercept" in dataset:
    intercept = dataset.RescaleIntercept

  slope = 0.0
  if "RescaleSlope" in dataset:
    slope = dataset.RescaleSlope 

  pixel_array = dataset.pixel_array
  if intercept != 0.0 and slope != 0.0:
    pixel_array = image*slope + intercept

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
    im = PIL.Image.frombuffer(mode, size, dataset.PixelData, "raw", mode, 0, 1)
  else:
    image = get_LUT_value(dataset.pixel_array, dataset.WindowWidth, dataset.WindowCenter)
    # Convert mode to L since LUT has only 256 values:
    # http://www.pythonware.com/library/pil/handbook/image.htm
    im = PIL.Image.fromarray(image).convert('L')

  return im, pixel_array


def get_LUT_value(data, window, level):
  """Helper function to get lookup-up table.

  This function is a direct copy from the pydicom library. See
  'contrib/pydicom_PIL.py'.
  """
  return np.piecewise(data,
                      [data <= (level - 0.5 - (window - 1) / 2),
                       data > (level - 0.5 + (window - 1) / 2)],
                      [0, 255, lambda data: ((data - (level - 0.5)) / (window - 1) + 0.5) * (255 - 0)])
