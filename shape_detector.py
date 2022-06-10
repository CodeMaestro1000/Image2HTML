import cv2, imutils, datetime


def sort_list(data, key):
    data.sort(key = lambda x: x[key][1])
    return data

def detect_shapes(image):
    """
    This function takes in an image (preferably after the original image has been processed to give a top-down view) and returns a 
    dictionary containing all the shapes detected, the location of the centroids and the dimensions (where applicable)

    For now the function can only detect rectangles, squares and circles. This is done by estimating the contour perimeters of the outline
    or shape in the image.

    Anything not inferred to be a square or rectangle is assumed to be a circle.
    """
    image = imutils.resize(image, height = 500) # resize image to have a height of 500px

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(image, (7, 7), 0) # applying a gaussian blur with a 7 x 7 kernel window to remove high freq noise from image to better detect edges
    # for more info on gaussian blur, see here: https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/

    # Applying adaptive thresholding using gaussian mean
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10) 

    # find contours in image
    contours = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours) # to account for how different versions of opencv return contours
    # contours = sorted(contours, key=cv2.contourArea, reverse=True)

    last_centroid = (0, 0)
    data_list = []

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

    data_list = sort_list(data_list, "centroid")
    shape = 'unknown'
    render_dict = {}
    delta = 5 # value that determines what is contained in a row
    rows = 0
    for data in data_list:
        c = data["contour"]
        centroid = data["centroid"]    
        contour_perimeter = cv2.arcLength(c, True)
    
        perimeter_approx = cv2.approxPolyDP(c, 0.01 * contour_perimeter, True)
        if len(perimeter_approx) < 9: # allowance since freehand drawing 
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w/float(h)
            shape  = 'square' if aspect_ratio >= 0.9 and aspect_ratio <= 1.5 else 'rectangle' # can play around with the values for aspect ratio
            shape_data = {"shape": shape, "centroid": centroid, "width": w, "height": h }
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255,0), 2)

        else:
            shape = 'circle'
            shape_data = {"shape": shape, "centroid": centroid, "width": None, "height": None}
            cv2.drawContours(image, [perimeter_approx], -1, (0, 0, 255), 2)
        
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
    
    cv2.namedWindow("Shapes")
    cv2.imshow("Shapes", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Shapes")
    return render_dict