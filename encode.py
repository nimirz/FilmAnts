# usage: python encode.py -o output_video.h265
# script modified from depthai tutorials

import depthai as dai
import cv2
import argparse
import subprocess
import os
from datetime import datetime
from pathlib import Path

# Construct argument parser and parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default="recordings", help="path to output video file")
ap.add_argument("-e", "--exposure", required=False, help="set exposure of camera")
ap.add_argument("-l", "--lens", required=False, help="set lens position of camera")
ap.add_argument("-i", "--iso", required=False, help="set ISO of camera")
ap.add_argument("-t", "--temp", required=False, help="set colour temperature for manual white balance")
ap.add_argument("-4k", "--record_4K", type=bool, required=False, default=False, help="record in 4K resolution")
ap.add_argument("-fps", "--frame_rate", type=float, required=False, default=30, help="set desired framerate")
ap.add_argument("-auto", "--auto_decode", type=bool, required=False, default=False,
                help="automatically produce mp4 file (requires ffmpeg to be installed)")

args = vars(ap.parse_args())

# Update camera settings
if args["lens"]:
    lensPos = int(args["lens"])
else:
    lensPos = 200

if args["exposure"]:
    expTime = int(args["exposure"])
else:
    expTime = 14000

if args["iso"]:
    sensIso = int(args["iso"])
else:
    sensIso = 1200

if args["temp"]:
    colourTemp = int(args["temp"])
else:
    colourTemp = 6000

# Step size for manual exposure/focus
EXP_STEP = 500
ISO_STEP = 50
LENS_STEP = 3
COL_STEP = 100

# Defaults and limits for manual focus/exposure controls
lensMin = 0
lensMax = 255

expMin = 1
expMax = 33000

sensMin = 100
sensMax = 1600

col_min = 1000
col_max = 12000

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam = pipeline.create(dai.node.ColorCamera)
# cam.setBoardSocket(dai.CameraBoardSocket.RGB)
if args["record_4K"]:
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
else:
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

cam.setPreviewSize(1280, 720)

# Create an encoder, consuming the frames and encoding them using H.265 encoding
videoEncoder = pipeline.createVideoEncoder()
videoEncoder.setDefaultProfilePreset(args["frame_rate"], dai.VideoEncoderProperties.Profile.H265_MAIN)
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


now = datetime.now()

save_path = Path.cwd() / args['path'] / f"{str(now.strftime('%Y-%m-%d'))}"
save_path.mkdir(parents=True, exist_ok=True)
video_name = str(save_path / f"{now.strftime('%Y-%m-%d_%H-%M-%S-%MS')}")

# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device, open(video_name + '.h265', 'wb') as videoFile:
    controlQueue = device.getInputQueue('control')
    ctrl = dai.CameraControl()
    ctrl.setManualExposure(expTime, sensIso)
    ctrl.setManualFocus(lensPos)
    ctrl.setManualWhiteBalance(colourTemp)
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
        elif key in [ord('h'), ord('j')]:
            if key == ord('h'): colourTemp -= COL_STEP
            if key == ord('j'): colourTemp += COL_STEP
            colourTemp = clamp(colourTemp, col_min, col_max)
            print("Setting manual whitebalance, kelvin:", colourTemp)
            ctrl = dai.CameraControl()
            ctrl.setManualWhiteBalance(colourTemp)
            controlQueue.send(ctrl)

    decode_command = "ffmpeg -framerate " + str(args["frame_rate"]) + " -i " + \
                    video_name + ".h265 -c copy " + \
                    video_name + ".mp4"
                     #args["path"][:-5] + now.strftime("%Y-%m-%d_%H-%M-%S-%MS.h265") + " -c copy " + \
                     #args["path"][:-5] + now.strftime("%Y-%m-%d_%H-%M-%S-%MS.mp4")

    if args["auto_decode"]:
        #ret = subprocess.run(decode_command, capture_output=True)
        os.system(decode_command)
        print("Processing output file...")
        print("\n\n Finished conversion!")
    else:
        print(
            "To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:")
        print(decode_command)
