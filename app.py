from flask import Flask, render_template, request, jsonify, url_for
import os
import base64
import cv2
import numpy as np
import math
from ultralytics import YOLO

app = Flask(__name__)

# 加載 YOLO 模型
yolo_model = YOLO('yolov8n.pt')  # 使用輕量版 YOLOv8 模型

os.makedirs('processed_images', exist_ok=True)

def process_image_with_yolo(image_data, dist_in_cm=30.0, dist_in_pixel=100.0):
    """
    使用 YOLO 模型處理圖像並計算物品尺寸
    """
    # 將 base64 解碼為圖像
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # 執行 YOLO 物件檢測
    results = yolo_model(image)

    # 計算每厘米的像素數
    pixel_per_cm = dist_in_pixel / dist_in_cm
    items = []

    recognized_objects = []  # 儲存辨識到的物體

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            label = result.names[int(box.cls[0])]
            confidence = box.conf[0]

            # 儲存辨識的物體名稱
            recognized_objects.append(label)

            # 打印辨識的物體和信心度
            print(f"Detected object: {label}, Confidence: {confidence:.2f}")

            # 計算物品尺寸
            width_px = x2 - x1
            height_px = y2 - y1
            width_cm = width_px / pixel_per_cm
            height_cm = height_px / pixel_per_cm

            # 假設深度固定為 15cm
            volume = width_cm * height_cm * 15
            print(f"{label} : {volume}")
            items.append(volume)

            # 在圖像上標記邊界框與尺寸
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image, f"{label} ({confidence:.2f})",
                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
            cv2.putText(
                image, f"{width_cm:.1f}cm x {height_cm:.1f}cm",
                (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
            )

    # 將處理後的圖像保存到本地檔案
    processed_image_path = "static/processed_image.jpg"
    cv2.imwrite(processed_image_path, image)

    # 將處理後的圖像轉換為 base64 編碼
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    print("Recognized objects:", recognized_objects)

    return processed_image_path, encoded_image, items

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/process', methods=['POST'])
def process():
    data_url = request.json.get('image')
    scale = request.json.get('scale', 'normal')

    # 設定每種 scale 的參數
    if scale == 'far':
        dist_in_cm = 30.0
        dist_in_pixel = 50  # 假設這是遠景對應的像素值
    elif scale == 'close':
        dist_in_cm = 30.0
        dist_in_pixel = 200  # 假設這是近景對應的像素值
    else:
        dist_in_cm = 30.0
        dist_in_pixel = 100.0  # 默認值

    image_data = base64.b64decode(data_url.split(',')[1])
    processed_image_path, processed_image, items = process_image_with_yolo(image_data, dist_in_cm, dist_in_pixel)

    if processed_image is None:
        return jsonify({'error': 'Image processing failed'})

    # 計算需要的箱子數量
    small, medium, large = fit_boxes(items)

    # 計算需要的車輛大小
    car = fit_car([small, medium, large])

    # 返回處理後的結果
    return jsonify({
        'processed_image': processed_image,  # Base64 圖片
        'image_path': url_for('static', filename='processed_image.jpg'),
        'small': small,
        'medium': medium,
        'large': large,
        'car': car,
        'redirect_url': url_for('home', preserve='true')
    })

def fit_car(box_list):
    """
    計算所需車輛大小
    """
    large = 69 * 47 * 47  
    medium = 48 * 45 * 42  
    small = 47 * 33 * 30 

    ret = large * box_list[2] + medium * box_list[1] + small * box_list[0]
    ret /= 1000000

    # 將 ret 設定為 0.5 的 ceiling
    ret = math.ceil(ret * 2) / 2
    return ret

def fit_boxes(items):
    """
    根據物品體積計算需要的箱子數量
    """
    large = 69 * 47 * 47  
    medium = 48 * 45 * 42  
    small = 47 * 33 * 30  

    r_small = 0
    r_medium = 0
    r_large = 0

    for tmp in items:
        while tmp >= large:
            tmp -= large
            r_large += 1
        while large > tmp >= medium:
            tmp -= medium
            r_medium += 1
        while medium > tmp >= small:
            tmp -= small
            r_small += 1

    if tmp > 0:
        r_small += 1

    return r_small, r_medium, r_large

if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', debug=True, port=5000, ssl_context=context)
