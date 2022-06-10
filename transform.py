import cv2, imutils, os
from skimage.filters.thresholding import threshold_local
import numpy as np
from four_point_transform import four_point_transform

image_path = 'Test Images/test_img_11.jpg'

# read in image
image = cv2.imread(image_path)


def nothing(x):
    pass

def get_top_down_view(image):
    original_image = image.copy()
    ratio = image.shape[0] / 500.0 # maintain aspect ratio for further processing
     # keep a copy of the original image
    image = imutils.resize(image, height = 500) # resize image to have a height of 500px

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0) # applying a gaussian blur with a 5 x 5 kernel window to remove high freq noise from image to better detect edges
    # for more info on gaussian blur, see here: https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/

    cv2.namedWindow("Edge Detection")
    cv2.createTrackbar("lower", "Edge Detection", 75, 100, nothing)
    cv2.createTrackbar("upper", "Edge Detection", 200, 400, nothing)
    
    edged = cv2.Canny(gray, 75, 200)
    # see info on edge detection here: https://pyimagesearch.com/2021/05/12/opencv-edge-detection-cv2-canny/

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

    cv2.drawContours(image, [outline], -1, (0, 255, 0), 2) # -1 parameter is to draw all contours, (0, 255, 0) is color, 2 is thickness
    # apply transform to original image and resize the outline based on the pre-computed aspect ratio

    cv2.namedWindow("Paper Outline")
    cv2.imshow("Paper Outline", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Paper Outline")
    warped = four_point_transform(original_image, outline.reshape(4, 2) * ratio)
    
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    return warped

def get_shape_from_contours(contour):
    shape = "unidentified"
    contour_perimeter = cv2.arcLength(contour, True)
    perimeter_approximation = cv2.approxPolyDP(contour, 0.04 * contour_perimeter, True) # common values for sigma (the second parameter) ranges btw 1 and 5%
    
    # if the shape is a triangle, it will have 3 vertices
    if len(perimeter_approximation) == 3:
        shape = "triangle"
		# if the shape has 4 vertices, it is either a square or
		# a rectangle
    elif len(perimeter_approximation) == 4:
		# compute the bounding box of the contour and use the
		# bounding box to compute the aspect ratio
        (_, _, w, h) = cv2.boundingRect(perimeter_approximation)
        ar = w / float(h)
		# a square will have an aspect ratio that is approximately
		# equal to one, otherwise, the shape is a rectangle
        shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
		# if the shape is a pentagon, it will have 5 vertices
    elif len(perimeter_approximation) == 5:
        shape = "pentagon"
		# otherwise, we assume the shape is a circle
    else:
        shape = "circle"
		# return the name of the shape
    return shape

def detect_shapes(image):
    # load the image and resize it to a smaller factor so that
    # the shapes can be approximated better
    image = get_top_down_view(image)
    resized = imutils.resize(image, width=300)
    ratio = image.shape[0] / float(resized.shape[0])

    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    # gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    # find contours in the thresholded image and initialize the
    # shape detector
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    for c in contours:
	# compute the center of the contour, then detect the name of the
	# shape using only the contour
        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        shape = get_shape_from_contours(c)
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (255, 255, 255), 2)

    return image

transformed_image = get_top_down_view(image)
cv2.imwrite("output_3.jpg", transformed_image)

"""
cv2.namedWindow("Image")
cv2.moveWindow("Image", 40, 30)
cv2.namedWindow("Transformed")
cv2.moveWindow("Transformed", 900, 30)

os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
cv2.imshow("Image", imutils.resize(original_image, height=500))
cv2.imshow("Transformed", imutils.resize(image, height=500))
cv2.waitKey(0)    """
cv2.destroyAllWindows()