from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
import base64
import cv2
import numpy as np
import math
from scipy.spatial.distance import euclidean
from imutils import perspective
from imutils import contours
import imutils
import sys


# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

def boxconfig():
    return {
        'small': {'width': 47, 'height': 33},
        'medium': {'width': 48, 'height': 45},
        'large': {'width': 69, 'height': 47}
    }

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_image(image_data, dist_in_cm=30.0, dist_in_pixel=100.0):
    # 读取和处理图像
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    edged = cv2.Canny(blur, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # 计算每厘米的像素数
    pixel_per_cm = dist_in_pixel / dist_in_cm

    # 找寻并排序轮廓
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)

    cv2.putText(image, "Ref size: {:.2f}cm".format(dist_in_cm), (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    items = []

    # 绘制其余轮廓并计算尺寸
    for cnt in cnts:
        box = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        area = cv2.contourArea(box)
        if area > dist_in_cm ** 2:
            (tl, tr, br, bl) = box
            cv2.drawContours(image, [box.astype("int")], -1, (0, 0, 255), 2)
            mid_pt_horizontal = (tl[0] + int(abs(tr[0] - tl[0]) / 2), tl[1] + int(abs(tr[1] - tl[1]) / 2))
            mid_pt_verticle = (tr[0] + int(abs(tr[0] - br[0]) / 2), tr[1] + int(abs(tr[1] - br[1]) / 2))
            wid = euclidean(tl, tr) / pixel_per_cm
            ht = euclidean(tr, br) / pixel_per_cm
            # 這邊預設物品深度是 30 公分。
            items.append(wid * ht * 25)
            # print(f"with = {wid}, hieght = {ht}")
            cv2.putText(image, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.putText(image, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # 将处理后的图像转换为base64编码
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    print("Encoded image size:", len(encoded_image))

    return encoded_image, items

def fit_boxes(items):
    large = 69 * 47 * 47  
    medium = 48 * 45 * 42  
    small = 47 * 33 * 30  

    r_small = 0
    r_medium = 0
    r_large = 0
	
    for tmp in items:
        print(tmp)
        while tmp >= large:
            tmp -= large
            r_large += 1

        print(tmp)
        while large > tmp >= medium:
            tmp -= medium
            r_medium += 1

        print(tmp)
        while medium > tmp >= small:
            tmp -= small
            r_small += 1

    if tmp > 0:
        r_small += 1

    print(r_small, r_medium, r_large)

    return r_small, r_medium, r_large

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     # 檢查是否有文件在請求中
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file = request.files['file']
#     # 如果用戶沒有選擇文件，瀏覽器也會
#     # 提交一個沒有文件名的空部分
#     if file.filename == '':
#         return redirect(request.url)
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return 'File successfully uploaded'
#     return 'Invalid file extension'


@app.route('/')
def home():
	return render_template('main.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/process', methods=['POST'])
def process():
    data_url = request.json.get('image')
    image_data = base64.b64decode(data_url.split(',')[1])
    processed_image, items = process_image(image_data)
    if processed_image is None:
        return jsonify({'error': 'Image processing failed'})
    print("Processed image generated")
   
    print(items)
    small, medium, large = fit_boxes(items)

    return jsonify({
        'processed_image': processed_image,
        'small': small,
        'medium': medium,
        'large': large,
        'redirect_url': url_for('home', preserve='true')
    })


if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    app.run(host='140.116.179.17', debug=True, port=5000, ssl_context=context)

