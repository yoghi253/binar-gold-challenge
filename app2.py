import re
import pandas as pd
import chardet
import sqlite3
import os

from fileinput import filename
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, make_response, redirect, url_for, flash, render_template
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from io import StringIO
from pathlib import Path
# import matplotlib.pyplot as plt
# import seaborn as sns

conn = sqlite3.connect('gold_binar2.db')
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('staticFiles','uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# print("APP_ROOT", APP_ROOT)
# print("UPLOAD_FOLDER", UPLOAD_FOLDER)


class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modelling'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

@swag_from('docs/home.yml', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    welcome_msg = {
        "version": "1.0.0",
        "message": "GOLD CHALLENGE",
        "author": "YOGHI ANANTO"
    }
    return jsonify(welcome_msg)

# Show cleansing result
# @swag_from("docs/hello_world.yml", methods=['GET'])
# @app.route('/', methods=['GET'])
# def hello_world():
#     json_response = {
#         'status_code': 200,
#         'description': "Menyapa dunia",
#         'data': "Hello World untuk kaum mendang mending"
#     }

#     response_data = jsonify(json_response)
#     return response_data

@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/text', methods=['GET'])
def text():
    json_response = {
        'status_code': 200,
        'description': "Original teks",
        'data': "Hallo apa kabar semua?"
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/text-clean', methods=['GET'])
def text_clean():
    json_response = {
        'status_code': 200,
        'description': "Original teks",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', "Hallo apa kabar semua?"),
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')
    text_clean = str(text).lower()
    text_clean1 = re.sub(r'[^a-zA-Z0-9]', " ", text_clean)
    print("text_clean", text_clean1)
    #connect to sqlite3
    conn = sqlite3.connect('gold_binar2.db')
    print("opened database successfully")
    
    conn.execute("INSERT INTO users (text, clean_text) VALUES (?,?)",(text, text_clean1))
    print("add database successfully")
    
    conn.commit()
    print("record create successfully")
    conn.close()
    print(text_clean1)
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data_raw':text, 
        'data_clean': text_clean1
    }
    return json_response
@swag_from("docs/File_processing.yml", methods=['POST'])
@app.route('/file-processing', methods=['POST'])
# def text_processing_file():
#     # df = pd.DataFrame({'text': text, 'text_tweet': text_clean})
#     # Upladed file
#     file = request.files.getlist('file')[0]

#     # Import file csv ke Pandas
#     df = pd.read_csv(file, encoding="ISO-8859-1")
#     print(df.columns)

#     # Ambil teks yang akan diproses dalam format list
#     texts = df.Tweet.to_list()
#     # texts = df.Tweet.to_list()
#     texts = df['Tweet'].to_list()
#     print("hasil to list\n",texts)

#     # Lakukan cleansing pada teks
#     cleaned_text = []
#     for text in texts:
#         cleaned_text.append(re.sub(r'[^a-zA-Z0-9]', '', text))
#     # lakukan perulangan atau looping untuk membersihkan data dan simpan ke variable cleaned_text 

#     json_response = {
#         'status_code': 200,
#         'description': "Teks yang sudah diproses",
#         'data': cleaned_text,
#     }

#     response_data = jsonify(json_response)
#     return response_data

def file_processing():
    file = request.files.get('upload_file')
    data_filename = secure_filename(file.filename)
    file.save = os.path.join(UPLOAD_FOLDER, data_filename)
    path = os.path.join(UPLOAD_FOLDER)


    file_path = os.path.join(path, data_filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as fopen:
            q = fopen.read()
            # print("q",q)
            
        df = pd.read_csv(StringIO(q), header=None)


        texts = df[0].to_list()
        # print("texts", texts)

        cleaned_text = []
        for text in texts:
            cleaned_text.append(re.sub(r'[^a-zA-Z0-9]', '', text))
            # print("cleaned_text", cleaned_text)

        json_response = {
            'status_code': 200,
            'description': "Teks yang sudah diproses",
            'data': cleaned_text,
        }

        response_data = jsonify(json_response)
        return response_data
    except Exception as q:
        json_response = {
            'status_code' : 415,
            'description'  : "type tidak di dukung, sudah yakin kalo ini uft-8?",
            'data': []
        }
        response_data = jsonify(json_response)
        
        return response_data
    
    

if __name__ == '__main__':
    app.run(debug=False)
