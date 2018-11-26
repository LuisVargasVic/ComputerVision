# USAGE
# python pass-tracker.py --video videos/Training.mp4 --tracker csrt

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
	
def intersects(x1, y1, w1, h1, x2, y2, w2, h2):
	right_x1 = x1 + (w1 * 0.5)
	top_y1 = y1 - (h1 * 0.5)
	left_x1 = x1 - (w1 * 0.5)
	bottom_y1 = y1 + (h1 * 0.5)

	right_x2 = x2 + (w2 * 0.5)
	top_y2 = y2 - (h2 * 0.5)
	left_x2 = x2 - (w2 * 0.5)
	bottom_y2 = y2 + (h2 * 0.5)
	closenessPos = 25
	closenessNeg = -25
	firstMatch = right_x1 - left_x2
	secondMatch = left_x1 - right_x2
	thirdMatch = top_y1 - bottom_y2 + 20
	fourthMatch = bottom_y1 - top_y2 + 20

	rightMatch = right_x1 - right_x2
	leftMatch = left_x1 - left_x2
	bottomMatch = bottom_y1 - bottom_y2

	print("1 Centroide: ("+str(x1)+","+str(y1)+","+str(w1)+","+str(h1)+")")
	print("1 Left-top :("+str(left_x1)+","+str(top_y1)+ ") 1 Right-top :("+str(right_x1)+","+str(top_y1)+")")
	print("1 Left-bottom :("+str(left_x1)+","+str(bottom_y1)+ ") 1 Right-bottom :("+str(right_x1)+","+str(bottom_y1)+")")
	print("2 Centroide: ("+str(x2)+","+str(y2)+","+str(w2)+","+str(h2)+")")
	print("2 Left-top :("+str(left_x2)+","+str(top_y2)+ ") 2 Right-top :("+str(right_x2)+","+str(top_y2)+")")
	print("2 Left-bottom :("+str(left_x2)+","+str(bottom_y2)+ ") 2 Right-bottom :("+str(right_x2)+","+str(bottom_y2)+")")
	print("Match: "+ str(firstMatch)+ " " + str(fourthMatch))
	print("Match: "+ str(secondMatch)+ " " + str(fourthMatch))
	print("Match: "+ str(firstMatch)+ " " + str(thirdMatch))
	print("Match: "+ str(secondMatch)+ " " + str(thirdMatch))
	print("Match: "+ str(rightMatch)+ " " + str(bottomMatch))
	print("Match: "+ str(leftMatch)+ " " + str(bottomMatch))
	return (firstMatch <= closenessPos and fourthMatch <= closenessPos and firstMatch >= closenessNeg and fourthMatch >= closenessNeg
	or secondMatch <= closenessPos and fourthMatch <= closenessPos and secondMatch >= closenessNeg and fourthMatch >= closenessNeg
	or firstMatch <= closenessPos and thirdMatch <= closenessPos and firstMatch >= closenessNeg and thirdMatch >= closenessNeg
	or secondMatch <= closenessPos and thirdMatch <= closenessPos and secondMatch >= closenessNeg and thirdMatch >= closenessNeg
	or rightMatch <= closenessPos and bottomMatch <= closenessPos and rightMatch >= closenessNeg and bottomMatch >= closenessNeg
	or leftMatch <= closenessNeg and bottomMatch <= closenessPos and leftMatch >= closenessNeg and bottomMatch >= closenessNeg)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())

# initialize a dictionary that maps strings to their corresponding
# OpenCV object tracker implementations
OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}
count = 0
has = False

# initialize OpenCV's special multi-object tracker
trackers = cv2.MultiTracker_create()

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# loop over frames from the video stream
text = "Please choose player and ball"
while True:
	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame

	# check to see if we have reached the end of the stream
	if frame is None:
		break

	# resize the frame (so we can process it faster)
	frame = imutils.resize(frame, width=600)
	(H, W) = frame.shape[:2]
	cv2.putText(frame, text, (10, H-300), 
		cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)

	# grab the updated bounding box coordinates (if any) for each
	# object that is being tracked
	(success, boxes) = trackers.update(frame)

	# loop over the bounding boxes and draw then on the frame
	for box in boxes:
		(x, y, w, h) = [int(v) for v in box]
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		cv2.putText(frame, "[{}, {}, {}, {}]".format(x, y, w , h), (x, y - 15), 
			cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
		(x1, y1, w1, h1) = [int(v) for v in boxes[len(boxes)-1]] 
		(x2, y2, w2, h2) = [int(v) for v in boxes[len(boxes)-2]] 
		intersection = intersects(x1, y1, w1, h1, x2, y2, w2, h2)
		print(intersection)
		if (intersection and w1 != w2):
			print(has)
			if has == True:
				go = 1
			else:
				count += 1
				print(has)
				print("Count: " + str(count))
			has = True
		else:
			has = False
		
		if h1 <= 20 and h2 <= 20:
			text = "Please add player"
		elif h1 >= 20 and h2 >= 20:
			text = "Please add ball"
		elif h1 != h2:
			text = "You can now count touches from player"
			cv2.putText(frame, "Player has touch the ball {} times".format(count), (10, H - 20), 
					cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
				
		


	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		box = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)


		# create a new object tracker for the bounding box and add it
		# to our multi-object tracker
		tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
		trackers.add(tracker, frame, box)

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# if we are using a webcam, release the pointer
if not args.get("video", False):
	vs.stop()

# otherwise, release the file pointer
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()