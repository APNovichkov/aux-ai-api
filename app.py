# Import python modules
import flask as fl
from flask import Flask, jsonify, request
import os
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import json
import subprocess

# Import modules
import init

# Define app
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# Switch for Production/Dev DB
is_production_db = False

# Setup DB
host = os.environ.get('MONGODB_URI', 'localhost:27017/auxio')
if is_production_db:
    print("Using Production DB")
    client_string = f'mongodb://admin:admin@{host}'
else:
    print("Using Development DB")
    client_string = f'mongodb://{host}'

client = MongoClient(client_string)
db = client.get_default_database()
favorites = db['favorites']

# Initializations
composers = init.init_composers()
generators = init.init_generators(composers)


@cross_origin()
@app.route('/generate', methods=['GET'])
def generate():
    """Generate file and return its ID"""
    composer_name = request.args.get('composerName')
    num_notes = request.args.get('numNotes')

    mp3_fp, song_id = generators[composer_name].generate_song(num_notes)

    response_data = {
        "song_id": song_id
    }

    return jsonify(response_data)

@cross_origin()
@app.route('/get-file/<song_id>', methods=['GET'])
def get_file(song_id):
    """Return the mp3 file"""

    fp = os.path.join('mp3_files', f'{song_id}.mp3')

    print(f"Returning file: {fp}")

    return fl.send_file(
        fp,
        mimetype="audio/mp3",
    )

@cross_origin()
@app.route('/composers', methods=['GET'])
def get_composers():
    return jsonify({
        "composers": json.dumps(list(composers.keys()))
    })

@cross_origin()
@app.route('/<composer>/sample', methods=['GET'])
def get_sample_mp3(composer):
    """Return sample mp3 for given composer"""

    fp = os.path.join("sample_music", f'{composer}_sample.mp3')

    return fl.send_file(
        fp,
        mimetype="audio/mp3",
    )

@cross_origin()
@app.route('/convert', methods=['GET'])
def sample_convert():

    fp = os.path.join("sample_music", 'sample.mid')
    o_fp = os.path.join("sample_music", 'samplesssss.mp3')

    command = f"timidity {fp} -Ow -o - | ffmpeg -y -f wav -i - {o_fp}"

    print(f"Running command: {command}")

    subprocess.call(command, shell=True)

    print(f"Ran command!!")

    if os.path.exists(o_fp):
        print(f"{o_fp} is a valid path!!")

    return fl.send_file(
        o_fp,
        mimetype="audio/mp3",
    )



@cross_origin()
@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "You are in the index route for aux.io"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

