# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request, jsonify,url_for,redirect,flash
import json
import pandas as pd
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/contry')
def contry():
    return render_template('contry.html')

@app.route('/save-json', methods=['POST'])
def save_json():
    data = request.get_json()

    # Save the updated JSON data to post.json
    with open('static/post.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    logistics_file = request.files.get('logistics_file')
    store_file = request.files.get('store_file')

    if not logistics_file or not store_file:
        return "Both files are required."

    if allowed_file(logistics_file.filename) and allowed_file(store_file.filename):
        logistics_filename = secure_filename(logistics_file.filename)
        store_filename = secure_filename(store_file.filename)

        logistics_file_path = os.path.join(app.config['UPLOAD_FOLDER'], logistics_filename)
        store_file_path = os.path.join(app.config['UPLOAD_FOLDER'], store_filename)

        logistics_file.save(logistics_file_path)
        store_file.save(store_file_path)

        # 解析物流文件的第2列
        logistics_df = pd.read_excel(logistics_file_path)
        column2_values = logistics_df.iloc[:, 2].tolist()
        contry_values = logistics_df.iloc[:, 5].tolist()
        contry_values = list(set(contry_values))

        contryData = None
        with open('static/post.json', 'r') as f:
            contryData = json.load(f)
        noConfigArray = []
        for string in contry_values:
            if string in list(contryData.keys()):
                break
            else:
                noConfigArray.append(string)
        if noConfigArray.count() != 0:
            return render_template("redirect.html",strings=noConfigArray)

        # 在店铺文件中查找对应的值所在的sheet名字
        store_df = pd.read_excel(store_file_path, sheet_name=None)

        result_data = []
        for sheet_name, sheet_data in store_df.items():
            if not sheet_data.empty and '店' in sheet_name and sheet_data.shape[1] > 0:
                for index, row in sheet_data.iterrows():
                    orderId =  row.iloc[3]
                    if orderId in column2_values:
                        found_data = {
                            'sheet_name': sheet_name,
                            'column1_value':orderId,
                            'column6_value': str(row.iloc[1]).replace('.', '')
                        }
                        result_data.append(found_data)


        # 删除上传的文件，如果你想保留文件，可以注释掉下面这行
        os.remove(logistics_file_path)
        os.remove(store_file_path)

        return render_template('result.html', result=result_data)

    return "File type not allowed"

if __name__ == '__main__':
    app.run(debug=True)
