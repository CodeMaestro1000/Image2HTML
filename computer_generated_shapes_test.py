import numpy as np
import cv2

canvas = np.zeros((300,300,3), dtype=np.uint8)
canvas.fill(255)

black = (10, 10, 10)
cv2.rectangle(canvas, (10, 10), (60, 60), black)
cv2.rectangle(canvas, (50, 200), (200, 225), black, 5)
cv2.circle(canvas, (100, 130), 50, black, 2)
cv2.imshow("Canvas", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("generated_shapes.png", canvas)