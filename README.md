# FilmAnts
We are recording using [OAK-D cameras](https://shop.luxonis.com/products/1098obcenclosure) which are powerful cameras that allow us to run neural networks on board. There are 3 cameras on the device: a central 4K color camera, plus left and right 720p mono cameras that enable depth perception. This script allows you to do a basic 1080p recording using the central camera and control the camera settings using keystrokes. For more information check out the DepthAI [documentation](https://docs.luxonis.com/en/latest/).

## Getting Started:
1. Clone this repository to the computer you will be recording from.

2. Make sure you have Python and Anaconda (Python package management system) installed. I recommend the [miniconda](https://docs.conda.io/en/latest/miniconda.html) installation.

2. Create a new conda environment and install required packages using **`requirements.txt`**.
Open a terminal and run the following commands:\
a. Create the environment: `conda create --name FilmAnts` \
b. Activate the environment `conda activate FilmAnts` \
c. Install required packages: `pip install -r requirments.txt`

## Recording:
There are two scripts for recording. The `encode.py` saves both h265/h264 videos and mp4 videos and allows manipulation of camera settings, while `record.py` only saves mp4 videos. Use `record.py` when generating training data, as it allows clicking on the preview screen to record timepoints. 

### Procedure for `encode.py`:

1. To begin recording type: \
`python encode.py` 

This will launch a preview window where you can see what is being recorded and save the output in the provided location.

2. **Camera setings**: the following keystrokes allow you to change settings on the camera \
\
*Lens Position*: **,** increases and **.** decreases \
*Exposure*: **o** increases and **i** decreases \
*ISO*: **l** increases and **k** decreases \
 
 The values for each camera setting will be printed out in the console. After noting the values that work well for the camera setup, you can begin the recording with these settings by adding the optional arguments: \
 `python encode.py --exposure exp_value --iso iso_value --lens lens_position`
 
 3. Press `q` to end the recording.
 
 4. The default is for the file to be saved as an .h265 file. To convert to .mp4 use ffmpeg, or have it automatically be decoded to mp4 with the flag -auto True.
 
5. The videos will be saved under /recordings/date/ if the path is not specificed (see below for specifying path). The video filename will be `date-time.mp4`

6. Optional arugments: \
-p or --path: specify output path for saving videos. Default is recordings/date/ \
-4k or --record_4K: specify true to record in 4K, default is 1080p \
-fps or --frame_rate: specify the frame rate, default is 30fps
 
### Procedure for `record.py`: 
1. To begin recording type: `python record.py` and this will bring up a preview screen. Allow the camera to focus automatically, then press `r` to begin recording.

2. Click the screen to write the current frame, and X/Y coordinates of the location clicked to a csv file. This file will be saved in the specificed output folder. 

3. Press `s` to stop the recording.
 
4. You can press `r` again to begin another recording, or `q` to end.

5. The videos will be saved under /recordings/date/ if the path is not specificed (see below for specifying path). Each time the script is called the files will be saved under a new folder with the date. The video filename will be `date-time.mp4`. If a csv file is created, it will be saved with the same name.

6. Optional arugments: \
-p or --path: specify output path for saving videos. Default is recordings/date/ \
-fc or --frame_cnt: specify number of frames to record. Default is record until stopped by `s` or `q`. 

## Metadata for videos
For each video recorded, keep track of the filming conditions in a spreadsheet. Important things to note are date, time of recording, camera distance, walking substrate, and trail width, as well as any experimental alterations. Save this as a csv within the recordings folder.

