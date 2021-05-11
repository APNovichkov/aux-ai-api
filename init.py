from composer import Composer
from generator import Generator
import json
import os
import boto3

# Define Constants
SUFFIX = "seqlen_40_2LSTM_1Attention_2Dense.hdf5"
COMPOSERS = {
    'tchaikovsky': {
        'model_fp': os.path.join('models', f'tchaikovsky_{SUFFIX}'),
        'network_object_fp': os.path.join('network_objects', 'tchaikovsky_network_object.json'),
        'meta': '100seqlen2lstm1Attention2dense'
    },
    'rachmaninov': {
        'model_fp': os.path.join('models', f'rachmaninov_{SUFFIX}'),
        'network_object_fp': os.path.join('network_objects', 'rachmaninov_network_object.json'),
        'meta': '100seqlen2lstm1Attention2dense'
    },
    'chopin': {
        'model_fp': os.path.join('models', f'chopin_{SUFFIX}'),
        'network_object_fp': os.path.join('network_objects', 'chopin_network_object.json'),
        'meta': '100seqlen2lstm1Attention2dense'
    }
}

NETWORK_OBJECT_DIR = "network_objects"
MODEL_FOLDER = 'models'

# Init AWS S3 things
s3_client = boto3.client('s3',
                         aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                         aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
S3_BUCKET = 'andrey-aux-ai'


def init_composers():
    """Initalize composers and return dictionary with result"""

    # Create Model folder if it doesnt exist
    if not os.path.exists(MODEL_FOLDER):
        os.mkdir(MODEL_FOLDER)

    out = {}

    for name, fps in COMPOSERS.items():
        # Download model if it doenst exist yet
        if not os.path.exists(fps['model_fp']):
            _download_model(S3_BUCKET, os.path.basename(fps['model_fp']))

        # Get Network Object for this composer
        with open(fps['network_object_fp'], 'r') as f:
            data = json.load(f)

        print(f"Initializing composer: {name}")
        print(f"NI Shape: {data['network_input_shape']}\nSequence Length: {data['sequence_length']}\nNum_Vocab: {data['n_vocab']}")

        new_composer = Composer(name=name,
                                model_fp=fps['model_fp'],
                                network_input=data['network_input'],
                                network_input_shape=data['network_input_shape'],
                                pitch_names=data['pitch_names'],
                                sequence_length=data['sequence_length'],
                                n_vocab=int(data['n_vocab']))

        out[name] = new_composer

    return out


def init_generators(composers):
    """Initialize generators and return dictionary with result"""

    out = {}

    for name, composer in composers.items():
        new_generator = Generator(composer)
        out[name] = new_generator

    return out


def _download_model(s3_bucket, s3_key):
    output_fp = os.path.join('models', os.path.basename(s3_key))
    print(f"Downloading: s3://{s3_bucket}/{s3_key}")
    s3_client.download_file(s3_bucket, s3_key, output_fp)
    print(f'Downloaded {s3_key} to {output_fp}')
    return output_fp



