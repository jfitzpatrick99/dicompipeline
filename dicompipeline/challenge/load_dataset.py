"""
Module containing function to load a dataset from a given data directory.
"""
import os
import csv
from dicompipeline.challenge.parsing import parse_contour_file, parse_dicom_file, poly_to_mask
from PIL import Image, ImageDraw
import logging

def load_dataset(data_dir, idir):
  """Load the dataset from the given data directory and use the provided intermediate directory to
  store intermediate files for debugging purposes.

  :param data_dir: data directory to load the dataset from
  :param idir: intermediate directory to use for debugging. If set to None then no intermediate images are generated.
  """

  logging.info("Starting pipeline using data from data_dir " + data_dir)

  dataset = []

  links_filename = os.path.join(data_dir, "link.csv")
  with open(links_filename, "r") as links_file:
    links_reader = csv.DictReader(links_file)
    for row in links_reader:
      patient_id = row["patient_id"]
      original_id = row["original_id"]

      dicom_files_dir = os.path.join(data_dir, "dicoms", patient_id)
      i_contour_files_dir = os.path.join(data_dir, "contourfiles", original_id)

      logging.info("Processing dicom files in dir {} linked to contour files in dir {}".format(dicom_files_dir, i_contour_files_dir))

      dicom_filenames = os.listdir(dicom_files_dir)

      for dicom_filename in dicom_filenames:
        actual_dicom_filename = os.path.join(dicom_files_dir, dicom_filename)
        dicom_dict = parse_dicom_file(actual_dicom_filename)

        if dicom_dict is not None:
          image = dicom_dict["pixel_data"]
          width = len(image[0])
          height = len(image)

          if "instance_number" in dicom_dict:
            i_contour_filename = os.path.join(i_contour_files_dir, "i-contours", "IM-0001-{0:04d}-icontour-manual.txt".format(int(dicom_dict["instance_number"])))

            if os.path.isfile(i_contour_filename):
              i_contour_coords = parse_contour_file(i_contour_filename)
              i_contour_mask = poly_to_mask(i_contour_coords, width, height)

              if idir is not None:
                pil_image = Image.fromarray(image, mode="L")
                pil_image.save(os.path.join(idir, "{0}-{1}-{2:04d}-image.png".format(patient_id, original_id, int(dicom_dict["instance_number"]))))

                ImageDraw.Draw(pil_image).polygon(xy=i_contour_coords, outline=255)

                pil_image.save(os.path.join(idir, "{0}-{1}-{2:04d}-image_with_contour.png".format(patient_id, original_id, int(dicom_dict["instance_number"]))))

              dataset.append([image, i_contour_mask])
            else:
              logging.debug("No contour file for dicom file {}".format(actual_dicom_filename))
          else:
            logging.warning("dicom image {} is missing InstanceNumber tag in meta-data.".format(actual_dicom_filename))
        else:
          logging.warning("dicom file {} is invalid.".format(actual_dicom_filename))

  return dataset
