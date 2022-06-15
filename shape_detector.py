import cv2, imutils, logging


logging.basicConfig(level=logging.WARNING)

def sort_list(data, key):
    data.sort(key = lambda x: x[key][1])
    return data

def detect_shapes(image, duplicate_threshold=6, delta=5, show_output=True):
    """
    This function takes in an image (preferably after the original image has been processed to give a top-down view) and returns a 
    dictionary containing all the shapes detected, the location of the centroids and the dimensions (where applicable)

    For now the function can only detect rectangles, squares and circles. This is done by estimating the contour perimeters of the outline
    or shape in the image.

    Anything not inferred to be a square or rectangle is assumed to be a circle.

    The delta value determines what is contained in a row. It is a threshold value. If the difference of the vertical (y) component of the
    centroids of two shapes is less than delta, then the shapes are considered to be on the same row
    """
    data_list = [] # for storing contour data
    shape = 'unknown'
    shape_layout = {} # for saving data after arranging into rows and columns
    rows = 0
    last_centroid = (0, 0)
    render_dict = {} # for storing final form data

    image = imutils.resize(image, height = 500) # resize image to have a height of 500px
    if len(image.shape) >= 3: # change to grayscale if image is colored
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    gray = cv2.GaussianBlur(image, (7, 7), 0) # applying a gaussian blur with a 7 x 7 kernel window to remove high freq noise from image to better detect edges
    # for more info on gaussian blur, see here: https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/

    # Applying adaptive thresholding using gaussian mean
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10) 

    # find contours in image
    contours = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours) # to account for how different versions of opencv return contours
   
    # The following block of code process all the found contours.
    # If a contour has an area less than 50, it is considered a contour from noise and not from a shape, hence it is discarded
    for c in contours:
        area = cv2.contourArea(c)
        if area < 50: # discard smaller contours as they may just be as a result of noise
            continue

        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        contour_data = {"centroid": tuple([cX, cY]), "contour": c}
        data_list.append(contour_data)
    
    data_list = sort_list(data_list, 'centroid') # sort list in ascending order by y-axis of centroids
    for data in data_list:
        c = data["contour"]
        centroid = data["centroid"]    
        contour_perimeter = cv2.arcLength(c, True)

        # perform shape detection with Douglas-Pecker Algorithm
        # More info here: https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#ga0012a5fdaea70b8a9970165d98722b4c
        perimeter_approx = cv2.approxPolyDP(c, 0.01 * contour_perimeter, True)
        if len(perimeter_approx) < 9: # allowance since freehand drawing 
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w/float(h)
            shape  = 'square' if aspect_ratio >= 0.9 and aspect_ratio <= 1.5 else 'rectangle' # can play around with the values for aspect ratio
            shape_data = {"shape": shape, "centroid": centroid, "width": w, "height": h, 'perimeter': (x, y, w, h)}

        else:
            shape = 'circle'
            shape_data = {"shape": shape, "centroid": centroid, "width": None, "height": None, 'perimeter': [perimeter_approx]}
        
        """
        This block of code determines which inputs are on the same row. This computation is done based on a threshold value called delta.
        If the difference between the y-components of the two inputs are less than delta, then the inputs are considered to be on the same
        row
        """
        difference = abs(centroid[1] - last_centroid[1]) # |y2 - y1|
        if difference <= delta:
            try:
                shape_layout[f"row{rows}"].append(shape_data)
            except: shape_layout[f"row{rows}"] = [shape_data]
        else:
            rows += 1
            try:
                shape_layout[f"row{rows}"].append(shape_data)
            except: shape_layout[f"row{rows}"] = [shape_data]
        last_centroid = centroid

    # perform filtering on dictionary to remove duplicate values
    last_centroid = (0, 0)
    for key in shape_layout.keys():
        x = []
        last_centroid = (0, 0)
        # for each row, sort all shapes by the x component of the centroid and remove duplicate values
        # A duplicate is found is the difference between two x components is less than the duplicate_threshold. In that case, one shape is discarded
        for elem in sorted(shape_layout[key], key=lambda x: x['centroid'][0]): 
            centroid = elem['centroid']
            difference = centroid[0] - last_centroid[0]
            if abs(difference) > duplicate_threshold:
                x.append(elem)
            last_centroid = centroid
        render_dict[key] = x

    # For displaying intermediate output
    if show_output:
        for value in render_dict.values():
            for elem in value:
                centroid = elem['centroid']
                perimeter = elem['perimeter']
                shape = elem['shape']
                if shape == 'circle':
                    cv2.drawContours(image, perimeter, -1, (0, 0, 255), 2)
                else:
                    x = perimeter[0]; y = perimeter[1]; w = perimeter[2]; h = perimeter[3];
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255,0), 2)
                elem['perimeter'] = None # discard perimeter data after use since it is no longer needed
                cv2.circle(image, centroid, 2, (0, 0, 255), 4)
                cv2.putText(image, shape, (centroid[0]+4, centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
        cv2.namedWindow("Shapes")
        cv2.imshow("Shapes", image)
        cv2.waitKey(0)
        cv2.destroyWindow("Shapes")
    if not render_dict:
        logging.warning("NO SHAPES FOUND!!!")
    return render_dict