import cv2
from transform import get_top_down_view
from shape_detector import detect_shapes
from form_generator import generate_output_html

image_path = 'Test Images/test_img_7.jpg'
output_filename = "test_output.html"
image = cv2.imread(image_path)

skip_top_down_process = False # set to true if you already have a cropped image of your form
# change to False if you don't want intermediate outputs but it is highly recommended that you leave it as True 
# because you might need to tweak some values for performing edge detection
show_output = True 

if not skip_top_down_process:
    warped_image = get_top_down_view(image, show_output=show_output)
    data = detect_shapes(warped_image, duplicate_threshold=2, delta=5, show_output=show_output) if warped_image is not None else None
else:
    data = detect_shapes(image, duplicate_threshold=2, delta=5, show_output=show_output)
if data:
    generate_output_html(data, output_filename)
# if no shape is found, no output file will be created
