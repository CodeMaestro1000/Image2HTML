import cv2
from transform import get_top_down_view
from shape_detector import detect_shapes
from form_generator import generate_output_html

image_path = 'Test Images/test_img_7.jpg'
output_filename = "test_output.html"
image = cv2.imread(image_path)

warped_image = get_top_down_view(image)
data = detect_shapes(warped_image)
generate_output_html(data, output_filename)
