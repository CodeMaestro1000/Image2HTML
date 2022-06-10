import cv2, imutils, os, datetime
import numpy as np


def nothing(x):
    pass

def sort_list(data, key):
    data.sort(key = lambda x: x[key][1])
    return data

image_path = 'output_3.jpg'

# read in image
image = cv2.imread(image_path) 

ratio = image.shape[0] / 500.0 # maintain aspect ratio for further processing
original_image = image.copy() # keep a copy of the original image
image = imutils.resize(image, height = 500) # resize image to have a height of 500px

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0) # applying a gaussian blur with a 7 x 7 kernel window to remove high freq noise from image to better detect edges
# for more info on gaussian blur, see here: https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/

# this section uses automatic values for determinng the threshold values for edge detection
# this is done by computing the median of the images and using this median to compute the upper and lower thresholds
# see here for more info: https://pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
"""sigma = 0.33
v = np.median(gray)
lower = int(max(0, (1.0 - sigma) * v))
upper = int(min(255, (1.0 + sigma) * v))
edged = cv2.Canny(gray, lower, upper) # applying canny edge detection to get outline of paper in image"""
# edged = cv2.Canny(gray, 75, 200)
# see info on edge detection here: https://pyimagesearch.com/2021/05/12/opencv-edge-detection-cv2-canny/"""
threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)

contours = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours) # to account for how different versions of opencv return contours
# contours = sorted(contours, key=cv2.contourArea, reverse=True)

last_centroid = (0, 0)
final_contours = []
final_centroids = []
data_list = []
last_contour = None

# The following block of code process all the found contours.
# If a contour has an area less than 50, it is considered a contour from noise and not from a shape, hence it is discarded
for c in contours:
    area = cv2.contourArea(c)
    if area < 50: # discard smaller contours as they may just be as a result of noise
        continue

    M = cv2.moments(c)
    cX = int((M["m10"] / M["m00"]))
    cY = int((M["m01"] / M["m00"]))
    centroid_difference = tuple([cX - last_centroid[0], cY - last_centroid[1]])
    if abs(centroid_difference[0]) > 5 or abs(centroid_difference[1]) > 5:
        # final_contours.append(c)
        # final_centroids.append(tuple([cX, cY]))
        data = {"centroid": tuple([cX, cY]), "contour": c}
        data_list.append(data)
    
    last_centroid = (cX, cY)
    last_contour = c

data_list = sort_list(data_list, "centroid")
cv2.namedWindow("Contours")
shape = 'unknown'
render_dict = {}
delta = 5 # value that determines what is contained in a row
rows = 0
for data in data_list:
    c = data["contour"]
    centroid = data["centroid"]    
    contour_perimeter = cv2.arcLength(c, True)
   
    perimeter_approx = cv2.approxPolyDP(c, 0.01 * contour_perimeter, True)
    outline = perimeter_approx
    if len(perimeter_approx) < 9: # allowance since freehand drawing 
        x,y,w,h = cv2.boundingRect(c)
        aspect_ratio = w/float(h)
        shape  = 'square' if aspect_ratio >= 0.9 and aspect_ratio <= 1.5 else 'rectangle' # can play around with this value
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255,0), 2)
        cv2.putText(image, str(aspect_ratio), (x, y+3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        shape_data = {"shape": shape, "centroid": centroid, "width": w, "height": h }
        # cv2.drawContours(image, [outline], -1, (0, 255, 0), 2)
        
    else:
        cv2.drawContours(image, [outline], -1, (0, 0, 255), 2)
        cv2.putText(image, str(len(perimeter_approx)), (centroid[0]+40, centroid[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        shape = 'circle'
        shape_data = {"shape": shape, "centroid": centroid, "width": None, "height": None}
    
    cv2.circle(image, centroid, 2, (0, 0, 255), 4)
    cv2.putText(image, shape, (centroid[0]+4, centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    
    difference = abs(centroid[1] - last_centroid[1]) # |y2 - y1|
    if difference <= delta:
        try:
            render_dict[f"row{rows}"].append(shape_data)
        except: render_dict[f"row{rows}"] = [shape_data]
    else:
        rows += 1
        try:
            render_dict[f"row{rows}"].append(shape_data)
        except: render_dict[f"row{rows}"] = [shape_data]
    

cv2.imshow("Contours", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
file_name = f"test_results/test_{datetime.datetime.now()}.jpg"
# cv2.imwrite(file_name, image)

for key, value in render_dict.items():
    print(f"{key} ==> {value}")
