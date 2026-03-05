import os

import numpy as np

os.environ['HF_HUB_OFFLINE'] = "1"
from sentence_transformers import SentenceTransformer



_transformer = SentenceTransformer('multi-qa-mpnet-base-cos-v1')

def vectorize(*args):
    if not args:
        return None
    avg_vector = np.mean([_transformer.encode(text) for text in args], axis=0)
    return avg_vector.tolist()
