from PIL import Image,ImageDraw
import os

########### showing the image on the screen
image1 = Image.open('icons/io.png')

drawing_object=ImageDraw.Draw(image1)
drawing_object.rectangle((50,0,190,150), fill = None, outline ='red')
image1.show()

#display(image1)