import cv2, imutils
import numpy as np
import logging

logging.basicConfig(level=logging.WARNING)

"""
By Dr. Adrian Rosebrock

See implementation details here: https://pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
"""

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def nothing(x):
    pass


def get_top_down_view(image, show_output=True):
    outline = None
    original_image = image.copy()
    ratio = image.shape[0] / 500.0 # maintain aspect ratio for further processing
     # keep a copy of the original image
    image = imutils.resize(image, height = 500) # resize image to have a height of 500px

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0) # applying a gaussian blur with a 5 x 5 kernel window to remove high freq noise from image to better detect edges
    # for more info on gaussian blur, see here: https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/

    edged = cv2.Canny(gray, 75, 200)
    # see info on edge detection here: https://pyimagesearch.com/2021/05/12/opencv-edge-detection-cv2-canny/

    if show_output:
        cv2.namedWindow("Edge Detection")
        cv2.createTrackbar("lower", "Edge Detection", 75, 100, nothing)
        cv2.createTrackbar("upper", "Edge Detection", 200, 400, nothing)
        while True:
            cv2.imshow("Edge Detection", edged)
            upper = cv2.getTrackbarPos("upper", "Edge Detection")
            lower = cv2.getTrackbarPos("lower", "Edge Detection")
            edged = cv2.Canny(gray, lower, upper)
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyWindow("Edge Detection")
    
    # find contours in edge detected image and use this contours to get the full outline of the paper
    contours = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # find contours manipulates the image passed in... be sure to make a copy of the image if you plan on using it again
    # RETR_LIST tells find contours to abandon any parent-child relationships in contours found
    # CHAIN_APPROX_SIMPLE only compresses the contours (removes redundant points) and saves memory
    # see more on contours here: https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html

    contours = imutils.grab_contours(contours) # to account for how different versions of opencv return contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5] # get the top 5 largest contours by area in descending order

    for c in contours:
        """
        arcLength() calculates a contour perimeter or curve length, the True flag tells the function that the perimeter is closed

        approxPolyDP() approximates the length of a polygonal curve, the 0.02 * peri is the approximation precision;
        0.02 was used here but this number can change depending on use case
        True tells approxPolyDP that the approximated curve is closed
        """
        contour_perimeter = cv2.arcLength(c, True)
        perimeter_approx = cv2.approxPolyDP(c, 0.02 * contour_perimeter, True)

        """
        since we've sorted our contours from largest to smallest, the first approximation that returns 4 (a contour with 4 points)
        would be the largest one and hence our paper in the image.
        We're making some assumptions here :)
        """
        if len(perimeter_approx) == 4: 
            outline = perimeter_approx
            break

    """
    The original image is what we'll use to obtain the top-down view. Hence we need to multiply the outline by the aspect ratio
    (remember the image was resized for faster processing)

    The outline was reshaped to suit the four_point_transform function implementation.

    We then apply thresholding to To obtain the black and white feel to the image, we then take the warped image, 
    convert it to grayscale and apply adaptive thresholding on
    """
    if outline is None:
        logging.warning("NO OUTLINE DETECTED!!!")
        return None

    if show_output:
        cv2.drawContours(image, [outline], -1, (0, 255, 0), 2) # -1 parameter is to draw all contours, (0, 255, 0) is color, 2 is thickness
        # apply transform to original image and resize the outline based on the pre-computed aspect ratio

        cv2.namedWindow("Paper Outline")
        cv2.imshow("Paper Outline", image)
        cv2.waitKey(0)
        cv2.destroyWindow("Paper Outline")
    
    warped = four_point_transform(original_image, outline.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    return warped

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

def generate_output_html(data, filename):
    rendering_data = {
        "rectangle": {
            "input_type": """<input type="text" class="form-control" placeholder="rectangle" aria-label="" aria-describedby="">""", 
            "name":"Text Input"
            },
        
        "square"   : {
            'input_type': """<input class="form-check-input" type="checkbox" value="" id="">""",
            'name':'Checkbox'
            },
        
        "circle"   : {'input_type': """<input class="form-check-input" type="radio" name="" id="">""", 'name':'Radio Button'} 
    }

    form_data = ''

    ext = filename.split(".")[-1]
    if ext != "html":
        filename += ".html"

    for keys in data.keys():
        form_data += """\n\t\t\t<div class="row mb-3">"""
        for element in data[keys]:
            input_data = rendering_data[element['shape']]['input_type']
            form_data += f"""
                <div class="col">
                    <label for="" class="form-label">{rendering_data[element['shape']]['name']}</label>
                    {input_data}
                </div>
            """
        form_data +=  '</div>'

    html = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

            <title>Image2HTML</title>
        </head>
        <body>
            <div class="container-sm mt-4">
                <form class="d-block mx-auto border p-4">
                    {form_data}
                </form>
            </div>

            <style>
                form {{
                    width: 85%;
                    background-color: #FFFF;
                    border-radius: 15px;
                }}

                body {{
                    background-color: #F5F5F5;
                }}
            </style>
        
            <!-- Option 1: Bootstrap Bundle with Popper -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
        </body>
        </html>

    """

    with open(f"{filename}", "w") as out_file:
        out_file.write(html)