import io
import picamera # Camera

#### THIS IS IMPORTANT FOR LIFE STREAMING ####
import logging
import socketserver
from threading import Condition
from http import server

#### THIS IS IMPORTANT FOR IMAGE PROCESSING ####
import numpy as np
import cv2

from pycoral.adapters import common
from pycoral.utils.edgetpu import make_interpreter

_NUM_KEYPOINTS = 17

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<img src="stream.mjpg" width="640" height="480" style="width:100%;height:100%;" />
</body>
</html>
"""

# This is where you specify the Deep Neural Network.
# Please put it in the same folder as the python file.
# --> this can go at the very beginning after import cv2 in the streaming file
interpreter = make_interpreter('movenet.tflite')
interpreter.allocate_tensors()


def myPoseDetection(img):

    # Convert to RGB, not needed for streaming
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #### --> needs to happen for each image ####
    # This resizes the RGB image
    resized_img = cv2.resize(img_rgb, common.input_size(interpreter))
    # Send resized image to Coral
    common.set_input(interpreter, resized_img)

    # Do the job
    interpreter.invoke()

    # Get the pose
    pose = common.output_tensor(interpreter, 0).copy().reshape(_NUM_KEYPOINTS, 3)

    height, width, ch = img.shape

    # Draw the pose onto the image using blue dots
    for i in range(0, _NUM_KEYPOINTS):
        cv2.circle(img,
                [int(pose[i][1] * width), int(pose[i][0] * height)],
                5, # radius
                (255, 0, 0), # color in RGB
                -1) # fill the circle

    return img


def myFaceDetection(img):
    
    det = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = det.detectMultiScale(gray, 
    scaleFactor=1.1, 
    minNeighbors=5, 
    minSize=(80, 80), # adjust to your image size, maybe smaller, maybe larger?
    flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in rects:
        # x: x location
        # y: y location
        # w: width of the rectangle 
        # h: height of the rectangle
        # Remember, order in images: [y, x, channel]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 20)


    return img, rects

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.frame_i = 0
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        
                        ### The image is encoded in bytes,
                        ### needs to be converted to e.g. numpy array
                        frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8),
                                             cv2.IMREAD_COLOR)
                        
                        
                        ###############
                        ## HERE CAN GO ALL IMAGE PROCESSING
                        ###############
                    
                        #frame, rects = myFaceDetection(frame)
                        self.frame_i = self.frame_i + 1
                        frame = myPoseDetection(frame)
                        
                        ### and now we convert it back to JPEG to stream it
                        _, frame = cv2.imencode('.JPEG', frame) 
                        
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True







# Open the camera and stream a low-res image (width 640, height 480 px)
with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    camera.vflip = True # Flips image vertically, depends on your camera mounting
    output = StreamingOutput() 
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000) # port 8000
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
