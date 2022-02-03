# filmAnts
We are recording ants using [OAK-D cameras](https://shop.luxonis.com/products/1098obcenclosure) which are powerful cameras that allow us to run neural networks on board. There are 3 cameras on the device, a central 4K color camera and left and right 720p mono cameras that enable depth perception. This script allows you to do a basic 1080p recording using the central camera and control the camera settings using keystrokes. For more information check out the DepthAi [documentation](https://docs.luxonis.com/en/latest/).

The following steps will get you started with recording:

1. **Environment Setup**: use **`filmAnts.yml`** to setup a conda environment to ensure all of the required packages are installed.

2. **Camera Setup**: connect the camera to your computer using a USB cable.

3. **Recording**: the script **`encode.py`** will encode h265 or h264 videos at 1080p and 30 frames per second. To begin recording, type 
`python encode.py --output /path/to/output_file.h265` in terminal This will launch a preview window where you can see what is being recorded. 

4. **Camera setings**: keystrokes allow you to change settings on the camera. \
\
*Lens Position*: **,** increases and **.** decreases \
*Exposure*: **o** increases and **i** decreases \
*ISO*: **l** increases and **k** decreases \
 *press **q** to end the recording* 
 
 5. **Convert to mp4**: use ffmpeg to convert h265 to mp4 (download ffmpeg from [here](https://www.ffmpeg.org/) if you do not have it). \
 `ffmpeg -framerate 30 -i /path/to/output_file.h265 -c copy /path/to/video.mp4`
