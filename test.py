import cv2
import base64
import numpy as np
from scipy.spatial.distance import euclidean
from imutils import perspective, contours
import imutils
import time
import math


def process_image(image, dist_in_cm=30.0, dist_in_pixel=200.0, min_area=500):
    """
    處理影像並過濾掉過小的檢測結果。
    
    :param image: 輸入影像
    :param dist_in_cm: 參考物體的實際大小（厘米）
    :param dist_in_pixel: 參考物體的像素大小
    :param min_area: 檢測的最小面積閾值（以像素為單位）
    :return: 處理後的影像與檢測到的物品清單
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (11, 11), 0)
    edged = cv2.Canny(blur, 175, 225)
    edged = cv2.dilate(edged, None, iterations=5)
    edged = cv2.erode(edged, None, iterations=0)

    # 計算每厘米的像素數
    pixel_per_cm = dist_in_pixel / dist_in_cm

    # 找尋並排序輪廓
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)

    items = []

    # 繪製其餘輪廓並計算尺寸
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        # 過濾掉過小的輪廓
        if area < min_area:
            continue

        box = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)

        (tl, tr, br, bl) = box
        cv2.drawContours(image, [box.astype("int")], -1, (0, 0, 255), 2)
        mid_pt_horizontal = (tl[0] + int(abs(tr[0] - tl[0]) / 2), tl[1] + int(abs(tr[1] - tl[1]) / 2))
        mid_pt_verticle = (tr[0] + int(abs(tr[0] - br[0]) / 2), tr[1] + int(abs(tr[1] - br[1]) / 2))
        wid = euclidean(tl, tr) / pixel_per_cm
        ht = euclidean(tr, br) / pixel_per_cm
        # 假設物品深度是 15 公分
        items.append(wid * ht * 15)

        cv2.putText(image, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv2.putText(image, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return image, items

def fit_car(box_list):
    large = 69 * 47 * 47  
    medium = 48 * 45 * 42  
    small = 47 * 33 * 30 

    ret = large * box_list[2] + medium * box_list[1] + small * box_list[0]
    ret /= 1000000

    # 將 ret 設定為 0.5 的 ceiling
    ret = math.ceil(ret * 2) / 2
    return ret

def fit_boxes(items):
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

    print(r_small, r_medium, r_large)

    return r_small, r_medium, r_large

# 實時鏡頭檢測程式
# 實時鏡頭檢測程式
def realtime_detection():
    cap = cv2.VideoCapture(0)  # 開啟默認攝影機
    if not cap.isOpened():
        print("無法開啟攝影機")
        return

    last_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法獲取攝影機影像")
            break

        # 處理攝影機畫面
        processed_frame, items = process_image(frame)

        # 計算箱數與車數
        box_list = fit_boxes(items)
        car_count = fit_car(box_list)

        # 每秒列印結果
        current_time = time.time()
        if current_time - last_time >= 1:
            print(f"箱數: {box_list}, 車數: {car_count}")
            last_time = current_time

        # 顯示處理後的畫面
        cv2.imshow("Object Detection", processed_frame)

        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    realtime_detection()