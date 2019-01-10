#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import copyfile
import sys
import getopt
import json
import os
import subprocess
import cv2
import numpy as np

# main program entry point - decode parameters, act accordingly
def main(argv):
    # attempt to parse commandline parameters
    try:
        opts, args = getopt.getopt(argv, "ho:n:d:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if opts is None:
        usage()
        sys.exit(2)

    oldTool = ''
    newTool = ''
    dirProc = ''

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt == '-o':
            oldTool = arg
        elif opt == '-n':
            newTool = arg
        elif opt == '-d':
            dirProc = arg

    if oldTool == '' or newTool == '' or dirProc == '':
        usage()
        sys.exit(2)

    processDir(oldTool, newTool, dirProc)


def processDir(oldCmd, newCmd, dirProc):
    with open(os.path.join(dirProc, 'params.txt'), 'r') as file:
        params = file.readline()

    paramList = [[newCmd, params, 'new', 'new']]
    pos = params.find('--legratio')
    paramList.append([oldCmd, params[:pos], 'old', 'old'])

    resDir = os.path.join(dirProc, 'res')
    if not os.path.exists(resDir):
        os.mkdir(resDir)

    lineFile = 'file'
    for filename in os.listdir(dirProc):
        if filename.endswith(('.jpg', '.png')):
            lineFile += '\t{}\t'.format(filename)
            files = []
            text = []
            for el in paramList:
                cnt, full = execute(el[0], el[1], os.path.join(dirProc, filename))
                text += ['{}:{}%({}triangles)'.format(el[3], full, cnt)]
                el[2] += ' \t{}%({})'.format(full, cnt)

                workDir = os.path.dirname(el[0])
                files += [getLastStage(workDir, os.path.join(resDir, filename))]

            concatImage(files[0], files[1], text[0], text[1], os.path.join(resDir, filename))

    with open(os.path.join(resDir, 'res.txt'), 'a') as file:
        file.write(lineFile + '\n')
        for el in paramList:
            file.write(el[2] + '\n')


def getLastStage(fromPath, dstPath):
    stage15 = ''
    stage16 = ''
    for file in os.listdir(fromPath):
        if "state_15" in file:
            stage15 = file
        if "state_17" in file:
            stage16 = file

    file = stage15 if stage16 == '' else stage16
    return os.path.join(fromPath, file)

    # concatImage(fromPath, fromPath, dstPath)
    # copyfile(fromPath, dstPath)


def concatImage(imageName1, imageName2, txt1, txt2, dstPath):
    color = (255, 0, 0)

    img1 = cv2.imread(imageName1)
    img2 = cv2.imread(imageName2)
    resImg = np.concatenate((img1, img2), axis=1)
    cv2.line(resImg, (img1.shape[1], 0), (img1.shape[1], img1.shape[0]), color, 4)

    cv2.putText(resImg, txt1,
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                color,
                3,
                cv2.LINE_AA)
    cv2.putText(resImg, txt2,
                (img1.shape[1] + 10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                color,
                3,
                cv2.LINE_AA)

    cv2.imwrite(dstPath, resImg)


def execute(cmd, params, filename):
    workDir, exe = os.path.split(cmd)
    cmd = "python3 {} {} -i {}".format(exe, params, filename)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = workDir)
    p.wait()

    out = p.stdout.readlines()
    str = ''
    for el in out:
        str += el.decode("utf-8")
    res = json.loads(str)
    return res['TriangleCount'], int(float(res['PercentFull'] * 100))


def usage():
    pass


# call main function
if __name__ == "__main__":
    main(sys.argv[1:])
