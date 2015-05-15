# Execute like:
# $ python playground.py | cvlc  --demux=rawvideo --rawvid-fps=30 --rawvid-width=1280 --rawvid-height=720  --rawvid-chroma=RV24 - :sout="#transcode{vcodec=mp2v,vb=10000,fps=30,width=1280,height=720} :http{dst=:8081/desk.ts}" :no-sout-rtp-sap :no-sout-standard-sap :ttl=1 :sout-keep :clock-jitter=0 :deinterlace-mode=linear :clock-synchro=1


import cv2, sys

source = 1
cap = cv2.VideoCapture(source)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
sys.stderr.write("{0}, {1}".format(FRAME_WIDTH, FRAME_HEIGHT))

while True:
    frame_loaded, frame = cap.read()
    if not frame_loaded:
        break

    sys.stdout.write(frame.tostring())
