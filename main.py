import cv2, argparse
from functions import get_top_down_view, detect_shapes, generate_output_html

parser =  argparse.ArgumentParser()
parser.add_argument("-i", "--image", required=True, help='Filename for input image')
parser.add_argument("-o", "--output_filename", required=True, help='Filename for output HTML')
parser.add_argument("-t", "--skip_perspective_transform", default=False, help='Skip processing of cropping region of interest')
parser.add_argument("-s", "--show_output", default=True, help="Show intermediate outputs")

args = vars(parser.parse_args())

image_path = args['image']
output_filename = args['output_filename']
image = cv2.imread(image_path)

skip_perspective_transform = args['skip_perspective_transform'] # set to true if you already have a cropped image of your form use False if you don't want intermediate outputs
# but it is highly recommended that you leave it as True  because you might need to tweak some values for performing edge detection
show_output = args['show_output']

if skip_perspective_transform:
    data = detect_shapes(image, duplicate_threshold=2, delta=5, show_output=show_output)
else:
    warped_image = get_top_down_view(image, show_output=show_output)
    data = detect_shapes(warped_image, duplicate_threshold=2, delta=5, show_output=show_output) if warped_image is not None else None
    
if data:
    generate_output_html(data, output_filename)
# if no shape is found, no output file will be created
