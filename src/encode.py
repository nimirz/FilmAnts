
# usage: python encode.py -o output_video.h265
# script modified from depthai tutorials

import depthai as dai
import cv2
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=False, help="path to output video file")
args = vars(ap.parse_args())

# Set manual camera settings
lensPos = 132
expTime = 33000
sensIso = 1050

# Step size for manual exposure/focus
EXP_STEP = 500
ISO_STEP = 50
LENS_STEP = 3

# Defaults and limits for manual focus/exposure controls

lensMin = 0
lensMax = 255

expMin = 1
expMax = 33000

sensMin = 100
sensMax = 1600


# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam = pipeline.create(dai.node.ColorCamera)
# cam.setBoardSocket(dai.CameraBoardSocket.RGB)
# cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setPreviewSize(1280, 720)

# Create an encoder, consuming the frames and encoding them using H.265 encoding
videoEncoder = pipeline.createVideoEncoder()
videoEncoder.setDefaultProfilePreset(1920, 1080, 30, dai.VideoEncoderProperties.Profile.H265_MAIN)
cam.video.link(videoEncoder.input)

# Create output
videoOut = pipeline.createXLinkOut()
videoOut.setStreamName('h265')
videoEncoder.bitstream.link(videoOut.input)

# create preview
previewOut = pipeline.createXLinkOut()
previewOut.setStreamName("preview")
cam.preview.link(previewOut.input)

# control queue
controlIn = pipeline.createXLinkIn()
controlIn.setStreamName('control')
controlIn.out.link(cam.inputControl)


def clamp(num, v0, v1):
    return max(v0, min(num, v1))


# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device, open(args["output"], 'wb') as videoFile:
    controlQueue = device.getInputQueue('control')
    ctrl = dai.CameraControl()
    ctrl.setManualExposure(expTime, sensIso)
    ctrl.setManualFocus(lensPos)
    controlQueue.send(ctrl)

    # Output queue will be used to get the encoded data from the output defined above
    q_rgb = device.getOutputQueue("preview")
    q_enc = device.getOutputQueue(name="h265", maxSize=30, blocking=True)


    while True:
        in_rgb = q_rgb.tryGet()

        while q_enc.has():
            q_enc.get().getData().tofile(videoFile)

        if in_rgb is not None:
            cv2.imshow("preview", in_rgb.getFrame())

        key = cv2.waitKey(1)

        if key == ord('q'):
            break
        elif key == ord('t'):
            print("Autofocus trigger (and disable continuous)")
            ctrl = dai.CameraControl()
            ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
            ctrl.setAutoFocusTrigger()
            controlQueue.send(ctrl)
        elif key == ord('f'):
            print("Autofocus enable, continuous")
            ctrl = dai.CameraControl()
            ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
            controlQueue.send(ctrl)
        elif key == ord('e'):
            print("Autoexposure enable")
            ctrl = dai.CameraControl()
            ctrl.setAutoExposureEnable()
            controlQueue.send(ctrl)
        elif key in [ord(','), ord('.')]:
            if key == ord(','): lensPos -= LENS_STEP
            if key == ord('.'): lensPos += LENS_STEP
            lensPos = clamp(lensPos, lensMin, lensMax)
            print("Setting manual focus, lens position:", lensPos)
            ctrl = dai.CameraControl()
            ctrl.setManualFocus(lensPos)
            controlQueue.send(ctrl)
        elif key in [ord('i'), ord('o'), ord('k'), ord('l')]:
            if key == ord('i'): expTime -= EXP_STEP
            if key == ord('o'): expTime += EXP_STEP
            if key == ord('k'): sensIso -= ISO_STEP
            if key == ord('l'): sensIso += ISO_STEP
            expTime = clamp(expTime, expMin, expMax)
            sensIso = clamp(sensIso, sensMin, sensMax)
            print("Setting manual exposure, time:", expTime, "iso:", sensIso)
            ctrl = dai.CameraControl()
            ctrl.setManualExposure(expTime, sensIso)
            controlQueue.send(ctrl)

    print("To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:")
    print("ffmpeg -framerate 30 -i video.h265 -c copy video.mp4")
