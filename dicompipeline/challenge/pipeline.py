"""
Module containing the model training pipeline.
"""
import logging
from sklearn.utils import shuffle


def run_pipeline(X_train, y_train, idir, n_epochs=10, batch_size=8):
  """Run the cardiac MRI image model training pipeline on the given data.

  :param X_train: Array of numpy images containing the input image data.
  :param y_train: Array of numpy boolean masks indicating where the contours
  are.
  :param idir: Intermediate directory to use to write debug data if the idir is
  not None.
  :param n_epochs: Number of epochs to train for.
  :param batch_size: Batch size for each forward/backward pass.
  :return: TODO: Yet to be determined.
  """
  num_samples = len(X_train)
  num_batches = int(num_samples / batch_size)
  if num_samples % batch_size != 0:
    num_batches = num_batches + 1

  logging.info("Number of samples: {}".format(num_samples))
  logging.info("Number of batches: {}".format(num_batches))

  for i in range(n_epochs):
    # shuffle the complete dataset on each epoch so that samples used for each
    # batch are randomly selected.
    X_train, y_train = shuffle(X_train, y_train)
    for j in range(num_batches):
      logging.info("Training on epoch {}, batch {}".format(i+1, j+1))
      batch_start = j * batch_size
      batch_end = batch_start + batch_size

      logging.info("Batch start is {}".format(batch_start))

      X_batch = X_train[batch_start:batch_end]
      y_batch = y_train[batch_start:batch_end]
      train_batch(X_batch, y_batch)
      logging.info("Finished training on epoch {}, batch {}".format(i+1, j+1))


def train_batch(X_train, y_train):
  """Train the given batch of samples.

  :param X_train: Batch of input samples.
  :param y_train: Batch of contour masks.
  :return: TODO: Yet to be determined.
  """

  logging.info("Training batch")
  logging.info("Size of this batch {}".format(len(X_train)))
  logging.info("Done training batch")
