import os, sys, shutil
import subprocess

month_directory = 'D:\\000006\\08\\'
for folder_name in os.listdir(month_directory):
    print(folder_name)
    os.chdir(os.path.join(month_directory, folder_name))
    os.mkdir("0")
    os.mkdir("1")
    os.mkdir("2")
    os.mkdir("3")
    subfolder_path = os.path.join(month_directory, folder_name)
    for file_name in os.listdir(subfolder_path):
        if "jpg" in file_name:
            imagename_array = file_name.split('-')
            folder = imagename_array[0]
            f = os.path.join(subfolder_path, file_name)
            print('f' + f)
            dest_folder = os.path.join(subfolder_path, folder)
            print('dest' + dest_folder)
            shutil.copy(f, dest_folder)

    for m in range(4):
        n = 0
        current_directory = os.path.join(month_directory, folder_name) + '\\' + str(m) + '\\'
        for file_name in os.listdir(current_directory):
            os.rename(os.path.join(current_directory, file_name), os.path.join(current_directory, str(n) + '.jpg'))
            n = n + 1
##                    cmd = 'ffmpeg -r 2 -f image2 -start_number 0 -i %01d.jpg -codec:v prores -profile:v 2 output'+str(m)+'.mov'
##
##                    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell = True)
##                    (output , error)= p.communicate()
##
##                    p_status = p.wait()
##                    print "Command output" + output