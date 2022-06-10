import cv2, imutils
from four_point_transform import four_point_transform




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