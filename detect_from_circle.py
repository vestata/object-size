# 在導入部分加入
import cv2
import numpy as np
import math
from scipy.spatial.distance import euclidean
from imutils import perspective
from imutils import contours
import imutils
import sys

def show_images(images):
    try:
        for i, img in enumerate(images):
            cv2.imshow("image_" + str(i), img)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Received Ctrl+C, exiting.")
    finally:
        cv2.destroyAllWindows()

if len(sys.argv) < 2:
    print("Usage: python init.py <dist_in_cm>")
    sys.exit(1)

dist_in_cm = float(sys.argv[1])

# 讀取和處理圖像
image = cv2.imread("images/000001.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (9, 9), 0)
edged = cv2.Canny(blur, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

# 使用霍夫變換檢測圓形
detected_circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=1, maxRadius=40)

# 找尋並排序輪廓
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
(cnts, _) = contours.sort_contours(cnts)

if detected_circles is not None:
    detected_circles = np.uint16(np.around(detected_circles))
    # 選擇最左邊的圓形作為參考
    leftmost_circle = sorted(detected_circles[0], key=lambda x: x[0])[0]
    cv2.circle(image, (leftmost_circle[0], leftmost_circle[1]), leftmost_circle[2], (0, 255, 0), 2)
    ref_radius = leftmost_circle[2]  # 參考半徑
    dist_in_pixel = 2 * ref_radius   # 參考物體直徑的像素長度
    pixel_per_cm = dist_in_pixel / dist_in_cm

    # 排除原來的第一個輪廓
    cnts = cnts[1:]
else:
    print("No circles detected. Using first contour as reference.")
    ref_object = cnts[0]
    box = cv2.minAreaRect(ref_object)
    box = cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    box = perspective.order_points(box)
    (tl, tr, br, bl) = box
    dist_in_pixel = euclidean(tl, tr)
    pixel_per_cm = dist_in_pixel / dist_in_cm
    cnts = cnts[1:]

cv2.putText(image, "Ref size: {:.2f}cm".format(dist_in_cm), (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

# 繪製其餘輪廓並計算尺寸
for cnt in cnts:
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
    cv2.putText(image, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    cv2.putText(image, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

show_images([image])

