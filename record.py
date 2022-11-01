from pathlib import Path
import csv
import argparse
from depthai_sdk import Previews
from depthai_sdk.managers import PipelineManager, PreviewManager, ArgsManager
import depthai as dai
import cv2
import time

def createFolder(path):
    recordings_path = path / f"{str(time.strftime('%Y-%m-%d'))}"
    if not recordings_path.is_dir():
        recordings_path.mkdir(parents=True, exist_ok=False)
        
    return recordings_path

# save points to csv
def recordFrameNum(x, y, frame_num, video):
    fn = video.rsplit('_', 1)[0] + '.csv'
    with open(fn, 'a+') as f:
        f.seek(0) 
        reader = csv.reader(f)
        nrow = len(list(reader)) # to number ants
        writer = csv.writer(f)

        if nrow == 0:
            # create header if file doesn't exist
            writer.writerow(['ant', 'frame', 'x', 'y', 'video']) 
        
        writer.writerow([nrow+1, frame_num, x, y, video.split('/')[-1]])

# click event function
def selectPoint(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Saving frame " + str(param[0])+ "; x="+str(x)+"; y="+str(y))
        recordFrameNum(x, y, param[0], param[1])

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-p', '--path', default="recordings", type=str, help="Path where to store the captured data")
parser.add_argument('-fc', '--frame_cnt', type=int, default=-1,
                    help='Number of frames to record. Record until stopped by default.')
args = ArgsManager.parseArgs(parser)

# create pipeline
pm = PipelineManager()

# define sources (can call left, right, and depth)
pm.createColorCam(xout=True, previewSize=(1920,1080))

def run():
    record_start = False
    first_record = True
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
                cv2.setMouseCallback("color", selectPoint, param=[frame_cntr, video_name])
                if args.frame_cnt == frame_cntr:
                    print("Stopping recording.")
                    frame_cntr = 0
                    record_start = False

            cv2.imshow("color", frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            # start the video recording:
            if key == ord('r'):
                print("Starting recording!")
                if first_record:
                    # specify save location
                    save_path = createFolder(Path.cwd() / args.path)
                    first_record = False
                record_start = True
                video_name = str(save_path) +'/' + time.strftime("%Y-%m-%d_%H-%M-%S")
                print("Saving to:"+video_name)
                writer = cv2.VideoWriter(video_name + ".mp4",cv2.VideoWriter_fourcc(*'mp4v'),
                                         30,(1920, 1080))
            
            if key == ord('s'):
                print("Stopping recording.")
                frame_cntr = 0
                record_start = False

    if record_start:
        writer.release()

if __name__ == '__main__':
    run()