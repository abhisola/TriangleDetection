# Rack Setup
This document is created for reference for setting up triangle detection racks.
## Installation
### Note Prerequisites
> 1.Enable VNC Server from the raspberry pi config
> 2.Setup Vnc Server with the credentials of realvnc
> 3.More detailed steps will be added later

### Update Raspbian by following commands
> Note: Execute One By One
```sh
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get dist-upgrade
$ sudo rpi-update
```

### Install Packages
```sh
$ sudo apt-get install fswebcam
$ sudo apt-get install gnome-schedule
$ sudo apt-get install libusb-dev
```

> If Unable to locate package error occurs run the following command again
```sh
$ sudo apt-get update
```
### Extra Package Only For Target Racks With PIR Sensor For Debugging Remotely
```sh
$ sudo apt-get install arduino
```
## One Line Install
```sh
sudo apt-get install fswebcam gnome-schedule libusb-dev arduino
```
### Setup Directory Structure
Create Folder With rack name. ex: Overland, Target 2

### Setup Hub Controller
> Note : The following hub controller program is tested with Dlink Hub.
1. Then Download Hub Ctrl from [Github](https://github.com/codazoda/hub-ctrl.c) or use the one this repository.
2. Copy hub-ctrl.c to the created rack folder
3. Run the following command in rack directory where you copied hub-ctrl.c
```sh
$ gcc -o hub-ctrl hub-ctrl.c -lusb
```
4. If the command creates another file named hub-ctrl no extension everything worked.

### Setup Code
1. create a file named camera.sh in rack name folder
2. copy paste the given code in camera.sh
3. open terminal in that folder and run the following command
```
$ chmod 755 camera.sh
```
> Note :
Test Cameras Before using the scheduler.
There needs to be few code changes that has to be done for the program to work.
Make sure everything is working before adding it to a scheduler.
Test Camera With The following command
```sh
$ fswebcam --device /dev/video0 -S 5 -D 3 --font sans:72 --no-banner -r 1280x720 --jpeg 65 image0.jpg
```
> Note :
Change Video Number and image name accordingly.
-S is Skip Frames
-D is Delay
-r is Resolution
Images will be saved in the same directory where you run this command!

### Setup Scheduler
1. Raspberry Start menu > System Tools > Scheduled tasks
2. Create New From New Button in tool bar
3. Select "A task that launches recurrently" button
4. Use "Camera" as description
5. In command box enter the following command
```sh
$ sudo bash /home/pi/${rack name folder}/camera.sh
```
6. Select Advance Radio Button
7. In minute field enter the following
```sh
*/15
```
> Note:
> The above will run camera.sh every 15minutes if you want to increase the minutes simply change the above to what ever minutes you want

### Util commands
| Command | Note |
| ------- | -------|
| ls /dev/video* | List All Video Devices Connected |
| lsusb | List All USB devices Connected |
| ls -l /dev/v4l/by-path/ | List Video Devices By path |
| ls -lrt | Check File Permissions |
| ls /dev/tty* | List All Serial Devices Connected |
