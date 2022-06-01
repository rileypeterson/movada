import tensorflow as tf
from tfx import v1 as tfx
from absl import logging
import os
import urllib.request
import tempfile


print("TensorFlow version: {}".format(tf.__version__))
print("TFX version: {}".format(tfx.__version__))


# PIPELINE_NAME = "penguin-simple"
#
# # Output directory to store artifacts generated from the pipeline.
# PIPELINE_ROOT = os.path.join("pipelines", PIPELINE_NAME)
# # Path to a SQLite DB file to use as an MLMD storage.
# METADATA_PATH = os.path.join("metadata", PIPELINE_NAME, "metadata.db")
# # Output directory where created models from the pipeline will be exported.
# SERVING_MODEL_DIR = os.path.join("serving_model", PIPELINE_NAME)
#
# logging.set_verbosity(logging.INFO)  # Set default logging level.
# DATA_ROOT = tempfile.mkdtemp(prefix="tfx-data")  # Create a temporary directory.
# _data_url = "https://raw.githubusercontent.com/tensorflow/tfx/master/tfx/examples/penguin/data/labelled/penguins_processed.csv"
# _data_filepath = os.path.join(DATA_ROOT, "data.csv")
# urllib.request.urlretrieve(_data_url, _data_filepath)
