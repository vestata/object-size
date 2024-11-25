import cv2
import base64
import numpy as np
from scipy.spatial.distance import euclidean
from imutils import perspective, contours
import imutils

def process_image(image, dist_in_cm=30.0, dist_in_pixel=100.0):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    edged = cv2.Canny(blur, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # 計算每厘米的像素數
    pixel_per_cm = dist_in_pixel / dist_in_cm

    # 找尋並排序輪廓
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)

    cv2.putText(image, "Ref size: {:.2f}cm".format(dist_in_cm), (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    items = []

    # 繪製其餘輪廓並計算尺寸
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
            # 假設物品深度是 15 公分
            items.append(wid * ht * 15)
            cv2.putText(image, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.putText(image, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return image, items

# 實時鏡頭檢測程式
def realtime_detection():
    cap = cv2.VideoCapture(0)  # 開啟默認攝影機
    if not cap.isOpened():
        print("無法開啟攝影機")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法獲取攝影機影像")
            break

        # 處理攝影機畫面
        processed_frame, items = process_image(frame)

        # 顯示處理後的畫面
        cv2.imshow("Object Detection", processed_frame)

        # 在終端列印物品體積
        print(f"物品體積: {items}")

        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    realtime_detection()