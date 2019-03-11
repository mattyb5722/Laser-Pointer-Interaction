import sys
import cv2
import numpy
import zmq
import socket
from time import time

from goprocam import GoProCamera
from goprocam import constants

from urllib.request import urlopen
import json

class LaserTracker(object):

    def setup_camera(self):
        """ Sets up Camera """
        # Webcam
        # self.capture = cv2.VideoCapture(0) # Set webcam as camera
        
        # GoPro
        gpCam = GoProCamera.GoPro()         # Connect to GoPro
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.t = time()                     # Set timer 
        gpCam.livestream("start")           # Start recording on GoPro
        self.capture = cv2.VideoCapture("udp://10.5.5.9:8554") # Set GoPro as camera
        
        if not self.capture.isOpened():     # Camera did not connect 
            sys.stderr.write("Faled to Open Capture device\n")
            sys.exit(1)                     # Exit the interaction

    def setup_blob_detector(self):
        """ Sets up Blob Detector """

        # Setup blob detector parameters.
        params = cv2.SimpleBlobDetector_Params()
         
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 2
        
        # Change thresholds
        params.minThreshold = 10;
        params.maxThreshold = 125;
        
        # Filter by Color
        params.filterByColor = True
        params.blobColor = 0
        
        # minDistBetweenBlobs = 10
        
        """
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.1
         
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.87
        """
        self.detector = cv2.SimpleBlobDetector_create(params) # Create a detector

    def handle_quit(self):
        """ Exit the interaction """
        self.capture.release()              # Release the camera connection
        cv2.destroyAllWindows()             # Close all display windows
        sys.stdout.write("Exited Successfully\n")
        sys.exit(0)                         # End program

    def detect_blobs(self, frame):
        """ Detect blobs """
        frame = cv2.convertScaleAbs(frame)
        keypoints = self.detector.detect(frame) # Detect blobs
        return keypoints                    # Return list of blob coordinates
    
    def display(self, frame, keypoints):
        """ Display the blobs in the picture """
        for point in keypoints:             # All the blobs
            loc = int(point.pt[0]), int(point.pt[1]) # Coordinates of blob
            cv2.circle(frame, loc, int(point.size/2)+5, (255, 255, 0), 2) 
                                            # Add circles around blobs
        cv2.imshow("Frame", frame)          # Display picture with blob circles
            
    def recieve_message(self, socket):
        """ Make connection with Unity. Check if Unity has ended """
        message = socket.recv()             # Recieve a message from Unity
        if message == b'END':               # If Unity has ended
            self.handle_quit()              # Exit the interaction
    
    def send_data(self, keypoints, socket):
        """ Send coordinates of blobs to Unity """
        self.recieve_message(socket)        # Make connection with Unity
        num_keypoints = str(len(keypoints)) # Convert number of blobs to a string
        socket.send(num_keypoints.encode()) # Send number of blobs to Unity
        
        for point in keypoints:             # All the blobs 
            loc = int(point.pt[0])-320, 240-int(point.pt[1]) # Coordinates of blob
            
            self.recieve_message(socket)    # Make connection with Unity
            Loc_x = str(loc[0])             # Convert x coordinates to a string
            socket.send(Loc_x.encode())     # Send x coordinates to Unity
            
            self.recieve_message(socket)    # Make connection with Unity
            Loc_y = str(loc[1])             # Convert y coordinates to a string
            socket.send(Loc_y.encode())     # Send y coordinates to Unity
 
    def go_pro_connection(self):
        """ Reset connection with GoPro """
        if time() - self.t >= 5:            # Every 5 seconds 
            self.sock.sendto("_GPHD_:0:0:2:0.000000\n".encode(), 
                             ("10.5.5.9", 8554)) # Sends message to GoPro
            self.t = time()                 # Reset timer         
 
    def run(self):
        self.setup_camera()                 # Setup the camera capture      
        self.setup_blob_detector()          # Setup blob detector
        
        context = zmq.Context()             # Set up connection with Unity
        socket = context.socket(zmq.REP)    # Set up connection with Unity
        socket.bind("tcp://*:5555")         # Connect to Unity
        
        while True:                         # Interaction is running
            success, frame = self.capture.read() # Take a picture
            if not success:                 # We could not take a picture
                sys.stderr.write("Could not read camera frame\n")
                sys.exit(1)                 # Exit the interaction
            
            self.go_pro_connection();       # Reset connection with GoPro
            keypoints = self.detect_blobs(frame) # Detect the blobs in the picture
            self.display(frame, keypoints)       # Display the blobs in the picture
            self.send_data(keypoints, socket)    # Send blob locations to Unity

            if cv2.waitKey(10) == 27:       # Key input of 'esc'
                self.handle_quit()          # Exit the interaction
                
if __name__ == '__main__':
    tracker = LaserTracker()                # Tracker object
    tracker.run()                           # Run interaction
