from pathlib import Path
import csv
import argparse
from depthai_sdk import Previews
from depthai_sdk.managers import PipelineManager, PreviewManager, ArgsManager
import depthai as dai
import cv2
import time

def createFolder(path):
        i = 0
        while True:
            i += 1
            recordings_path = path / f"{i}-{str(time.strftime('%Y-%m-%d'))}"
            if not recordings_path.is_dir():
                recordings_path.mkdir(parents=True, exist_ok=False)
                return recordings_path

# save points to csv
def recordFrameNum(x, y, frame_num):
    with open(save_path /'frame_list.csv', 'a') as f:
        writer = csv.writer(f)

        if f.tell() == 0:
            # create header if file doesn't exist
            writer.writerow(['frame', 'x', 'y'])

        writer.writerow([frame_num, x, y])

# click event function
def selectPoint(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Saving frame " + str(param)+ "; x="+str(x)+"; y="+str(y))
        recordFrameNum(x, y, param)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-p', '--path', default="recordings", type=str, help="Path where to store the captured data")
parser.add_argument('-fc', '--frame_cnt', type=int, default=-1,
                    help='Number of frames to record. Record until stopped by default.')
args = ArgsManager.parseArgs(parser)

# create pipeline
pm = PipelineManager()

# define sources (can call left, right, and depth)
pm.createColorCam(xout=True, previewSize=(1920,1080))

# specify save location
save_path = createFolder(Path.cwd() / args.path)       

def run():
    record_start = False
    frame_cntr = 0
    
    with dai.Device(pm.pipeline) as device:
        pv = PreviewManager(display=[Previews.color.name], mouseTracker=True)
        pv.createQueues(device)

        while True:
            pv.prepareFrames(blocking=True)
            frame = pv.get("color")
            #em.parseQueues()
            if record_start:
                writer.write(frame)
                frame_cntr += 1
                if args.frame_cnt == frame_cntr:
                    print("Stopping recording!")
                    frame_cntr = 0
                    record_start = False

            cv2.imshow("color", frame)
            cv2.setMouseCallback("color", selectPoint, param=frame_cntr)
            
            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            # start the video recording:
            if key == ord('r'): 
                print("Starting recording!")
                record_start = True
                fn = str(save_path) +'/' + time.strftime("%Y%m%d-%H%M%S") + ".mp4"       
                writer = cv2.VideoWriter(fn,cv2.VideoWriter_fourcc(*'mp4v'),
                                         30,(1920, 1080))
            
    if record_start:
        writer.release()

if __name__ == '__main__':
    run()