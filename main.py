import cv2
from transform import get_top_down_view
from shape_detector import detect_shapes
from form_generator import generate_output_html

image_path = 'Test Images/generated_shapes.png'
output_filename = "test_output.html"
image = cv2.imread(image_path)

skip_top_down_process = True

if not skip_top_down_process:
    warped_image = get_top_down_view(image)
    data = detect_shapes(warped_image)
else:
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except:
        pass
    data = detect_shapes(image)

generate_output_html(data, output_filename)
