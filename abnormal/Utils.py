import cv2
##

def as_filename(filename):
	clean_name = filename.replace("https://","")
	clean_name = clean_name.replace("http::","")
	clean_name = clean_name.replace("www.","")
	clean_name = clean_name.replace("/","-")
	clean_name = clean_name.replace(":","")

	return clean_name

def get_contours(image1):
	mono_difference = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
	(thresh, im_bw) = cv2.threshold(mono_difference, 0, 255, 1)
	contours, hierarchy = cv2.findContours(im_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	return contours


def get_diff_contourns(image1, image2):
	difference = cv2.subtract(image1, image2)

	contours = get_contours(difference)
	cv2.drawContours(difference, contours, -1, (0,255,0), 3)
	contours = get_contours(difference)

	return contours

def resize_images(image1, image2):
	(h1,w1,z) = image1.shape
	(h2,w2,z) = image2.shape
	if h1 < h2 or w1 < w2:
		image1.resize(image2.shape, refcheck=False)
	elif h2 < h1 or w2 < w1:
		image2.resize(image1.shape, refcheck=False)

def draw_contourns(image1, image2):
	contours = get_diff_contourns(image1,image2)

	areas = [cv2.contourArea(c) for c in contours]
	for i in range(len(contours) - 1):
		cnt=contours[i + 1]
		x,y,w,h = cv2.boundingRect(cnt)
		cv2.rectangle(image1,(x,y),(x+w,y+h),(0,255,0),3)

	return image1