'''
pip3 install boto3
create image.sh file
python3 /home/pi/{FolderName}/image.py
schedule image.sh to execute every 15min
Dont forget to raise the rights of image.py
chmod 755 image.py
'''
import boto3
import botocore
import subprocess
import os, shutil
import time
from os import path
from datetime import datetime

racknum = '000088'
home_folder = 'Olathe'
shelves = (0, 1, 2, 3)
today = datetime.today()
Y = today.year if today.year > 9 else '0' + str(today.year)
M = today.month if today.month > 9 else '0' + str(today.month)
D = today.day if today.day > 9 else '0' + str(today.day)
MM = today.minute if today.minute > 9 else '0' + str(today.minute)
H = today.hour if today.hour > 9 else '0' + str(today.hour)
bucket_name = 'my-rack'
temp_folder = 'temp'
temp_path = '/home/pi/'+home_folder+'/temp'

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

# Run -> lsusb -t and search hub port number and hub/4p or hub/7p
# Run -> lsusb -t |grep hub/7p |grep -o 'Dev [0-9]*' |grep -o '[0-9]*' to get dev number
# Change these variables according to hub
hub_dev_num = 6
hub_port_num = 4

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            print('Creating Folder')
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def emptyFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            print('Removing ' + the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def checkBucketExists():
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists


def checkFileExists(file):
    return path.exists(file)


def hubController(a=True):
    action = True if a else False
    msg = 'On' if a else 'Off'
    hubctrl = 'sudo /home/pi/{0}/hub-ctrl -b 001 -d {1} -P {2} -p {3}'.format(home_folder, hub_dev_num, hub_port_num, action)
    print('Command: ')
    print(hubctrl)
    print('\n')
    print('Turning {0} hub with Dev {1}, Port {2}'.format(msg, hub_dev_num, hub_port_num))

    process = subprocess.Popen(hubctrl, shell=True, stdout=subprocess.PIPE)
    print(process.stdout.read())


def main():
    # fsopts = "-S 5 -D 3 --font sans:72 --no-banner -r 1280x720 --jpeg 65"
    fsopts = "-S 30 -D 5 --font sans:50 --banner-colour 0xFF$racknum --line-colour 0xFF000000 -r 1280x720 --jpeg 65"

    for a in shelves:
        command = 'fswebcam --device /dev/video{0} {1} /home/pi/{2}/{3}/{4}.jpg'.format(str(a), fsopts, home_folder,
                                                                                         temp_folder, str(a))
        try:
            #hubController(False)
            #time.sleep(5)
            #hubController(True)
            print('\n')
            print('Taking Image With Command')
            print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            print(process.stdout.read())
            print('Image Taken')
            print('--------***---------')
            process.wait(60)
        except subprocess.TimeoutExpired:
            print('Timed Out For Video' + str(a))
            pass
        filename = str(a) + '-' + str(H) + str(MM) + '.jpg'
        path = racknum + '/' + str(Y) + '/' + str(M) + '/' + str(D) + '/' + filename
        local_path = '/home/pi/{0}/temp/{1}.jpg'.format(home_folder, str(a))
        if checkFileExists(local_path):
            if checkBucketExists():
                msg = 'Uploading Image On -> {0}-{1}-{2} {3}:{4}'.format(str(Y), str(M), str(D), str(H), str(MM))
                print(msg)
                s3.Object(bucket_name, path).put(Body=open(local_path, 'rb'))
                print('Done Uploading At ' + path)
                print('Now Sleeping for 5 Seconds')
                print('***')
                print('\n')
        time.sleep(5)
    emptyFolder(temp_path)


# call main function
if __name__ == "__main__":
    createFolder(temp_path)
    emptyFolder(temp_path)
    main()
