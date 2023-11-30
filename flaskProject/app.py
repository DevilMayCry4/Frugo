from flask import Flask, render_template, request
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
        column2_values = logistics_df.iloc[:, 1].tolist()

        # 在店铺文件中查找对应的值所在的sheet名字
        store_df = pd.read_excel(store_file_path, sheet_name=None)

        result_sheets = []
        for sheet_name, sheet_data in store_df.items():
            if not sheet_data.empty and sheet_data.shape[1] > 0:
                found_values = set(column2_values) & set(sheet_data.iloc[:, 0].tolist())
                if found_values:
                    result_sheets.append((sheet_name, list(found_values)))

        # 删除上传的文件，如果你想保留文件，可以注释掉下面这行
        os.remove(logistics_file_path)
        os.remove(store_file_path)

        return render_template('result.html', result=result_sheets)

    return "File type not allowed"

if __name__ == '__main__':
    app.run(debug=True)
