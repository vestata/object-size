from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # 檢查是否有文件在請求中
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # 如果用戶沒有選擇文件，瀏覽器也會
    # 提交一個沒有文件名的空部分
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File successfully uploaded'
    return 'Invalid file extension'

@app.route('/')
def home():
	return render_template('camera.html')

if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    app.run(host='140.116.179.17', debug=True, port=5000, ssl_context=context)

