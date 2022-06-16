# Image2HTML

This project uses computer vision to detect shapes in images and using these shapes to generate html forms styled with bootstrap css.

## How to use
- Specify an input image in main.py or use one of the images in the `Test Images` folder. Using the below image as an example:
![Test Image](https://drive.google.com/uc?export=view&id=14n4Qu-R2I7I46ke8-_FGz5rfQOl1hfK6)
- Run the `main.py` file.

### Edge Detection
- Use the trackbars to tune the values for edge detection until you can see the paper clearly as in the image below:
![Edge Detection Image](https://drive.google.com/uc?export=view&id=1-q4wJ2qX_yhpXqUnFlba78gG87ZYUw9o)

### Outline
- Enusre that the outline highlighted in green is the entire paper.
![Outline Image](https://drive.google.com/uc?export=view&id=1v1pP9AaLBq90r7VUl3IKMKcp4-7dMVOW)

### Obtain a top-down view of the paper in the image
![Top Down Image](https://drive.google.com/uc?export=view&id=1pShAXVjlZ-UgfPoIy9jiwkqUY41ybep3)

### Detect Shapes
- Preview all detected shapes
![Shape Detection Image](https://drive.google.com/uc?export=view&id=1zRh5VxHSRZJQFNhBqlXgmq89M4dvMcRQ/)

### Output
![Output HTML Image](https://drive.google.com/uc?export=view&id=1Kpu6uCXh-Pkz02wXDRyqeGQ6KXTLozGt)

### Important Notes
The quality of the input image largely determines the performance of the application. To get the best results, please use a plain paper and a thick pen to draw.

Also, to properly detect the outline of the paper, place the paper on a contrasting (relatively darker) background.

Please see the documentation.txt file for more information on this application.

CHEERS!!!
