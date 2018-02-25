"""Module defining deep learning pipeline for cardiac MRI images."""
import asyncio
import logging


class Pipeline:
  """Class implementing deep learning pipeline for cardiac MRI images."""

  def __init__(self, dataset, max_num_batches=10, loop=None):
    """Initialize the pipeline with the given dataset.

    :param dataset: Dataset to use as the source of training data.
    :param max_num_batches: Maximum number of batches to load in memory at
    once.
    :return: Pipeline instance initialized with the given dataset.
    """
    self._dataset = dataset

    if loop is None:
      self._loop = asyncio.get_event_loop()
    else:
      self._loop = loop

    self._queue = asyncio.Queue(loop=self._loop, maxsize=max_num_batches)


  def train(self, n_epochs=10, batch_size=10):
    """Run the cardiac MRI image model training pipeline on the given data.

    :param n_epochs: Number of epochs to train for.
    :param batch_size: Batch size for each forward/backward pass.
    :return: TODO: Yet to be determined.
    """
    num_samples = self._dataset.size()

    logging.info("Number of samples: {}".format(num_samples))

    for i in range(n_epochs):
      logging.info("Training epoch {}".format(i))
      producer = self.produce_batches(10)
      consumer = self.process_batches()
      self._loop.run_until_complete(asyncio.gather(producer, consumer))
      logging.info("Done training epoch {}".format(i))


  async def produce_batches(self, batch_size):
    """Produce batches where each batch has the given batch size.

    :param batch_size: Batch size to use for the batches.
    """
    async for batch in self._dataset.batches(batch_size):
      await self._queue.put(batch)

    await self._queue.put(None)


  async def process_batches(self):
      """Process each batch.

      Right now this just prints out the size of the batch.
      """
      while True:
        batch = await self._queue.get()
        if batch is None:
          break
        print(len(batch))

