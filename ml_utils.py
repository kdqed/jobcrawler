import os

#import numpy as np
from openai import OpenAI

import config
#os.environ['HF_HUB_OFFLINE'] = "1"
#from sentence_transformers import SentenceTransformer



#_transformer = SentenceTransformer('multi-qa-mpnet-base-cos-v1')
'''
def old_vectorize(*args):
    if not args:
        return None
    avg_vector = np.mean([_transformer.encode(text) for text in args], axis=0)
    return avg_vector.tolist()
'''

or_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.OPENROUTER_API_KEY,
)

def vectorize(*args):
    text_input = ' '.join(args)
    embedding = or_client.embeddings.create(
        model="perplexity/pplx-embed-v1-0.6b",
        input=text_input,
        encoding_format="float"
    )
    return embedding.data[0].embedding
    