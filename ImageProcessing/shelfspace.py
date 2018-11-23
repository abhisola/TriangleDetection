#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
import numpy as np
from tools.recognizer import TriRecognizeParams, TriRecognizer

# main program entry point - decode parameters, act accordingly
def main(argv):
    params = TriRecognizeParams()

    # attempt to parse commandline parameters
    try:
        opts, args = getopt.getopt(argv, "hi:b:ps",
                                   ["help", "arcmin=", "arcmax=", "areamin=", "areamax=", "paf=", "state", "nothresh",
                                    "legmin=", "legmax=", "legvar=", "expected=", "undistort=", "thresh=", "equhist"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if opts is None:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == '-p':
            print("Default parameter values")
            print("Minimum arc length: " + str(params.minArcLength))
            print("Maximum arc length: " + str(params.maxArcLength))
            print("Minimum triangle area: " + str(params.minArea))
            print("Maximum triangle area: " + str(params.maxArea))
            print("Polygon Approximation Factor: " + str(params.polyApproxFactor))
            print("Minimum leg length: " + str(params.minLegLength))
            print("Maximum leg length: " + str(params.maxLegLength))
            print("Maximum leg variation: " + str(params.maxLegVar))
            print("Expected triangle count: " + str(params.baseTriangleCount))
            sys.exit()
        elif opt == '-i':
            srcImageFile = arg
        elif opt == '-b':
            strBounds = arg
            params.useBounds = True
            splitBounds = strBounds.split(",")
            if len(splitBounds) != 8:
                print("Invalid boundary coordinates")
                usage()
                sys.exit(2)
            for i in range(0, 4):
                coord = [int(splitBounds[i * 2]), int(splitBounds[i * 2 + 1])]
                params.bounds.append(coord)
            params.bounds = np.array([params.bounds], np.int32)
            # print(bounds)
        elif opt == '--undistort':
            strDistort = arg
            params.useDistort = True
            splitDistort = strDistort.split(",")
            if len(splitDistort) < 4:
                print("Invalid undistort coefficients")
                usage()
                sys.exit(2)
            for i in range(0, len(splitDistort)):
                coeff = float(splitDistort[i])
                params.distortCoeffs[i, 0] = coeff
        elif opt == '-s':
            params.useSharpen = True
        elif opt == '--arcmin':
            params.minArcLength = int(arg)
        elif opt == '--arcmax':
            params.maxArcLength = int(arg)
        elif opt == '--areamin':
            params.minArea = int(arg)
        elif opt == '--areamax':
            params.maxArea = int(arg)
        elif opt == '--legmin':
            params.minLegLength = int(arg)
        elif opt == '--legmax':
            params.maxLegLength = int(arg)
        elif opt == '--legvar':
            params.maxLegVar = int(arg)
        elif opt == '--paf':
            params.polyApproxFactor = float(arg)
        elif opt == '--state':
            params.outputState = True
        elif opt == '--nothresh':
            params.useThreshold = False
        elif opt == '--thresh':
            params.useStaticThreshold = True
            params.staticThreshold = int(arg)
        elif opt == '--expected':
            params.baseTriangleCount = int(arg)
        elif opt == '--equhist':
            params.equalizeHist = True

    if srcImageFile == '':
        usage()
        sys.exit(2)

    TriRecognizer.processImage(srcImageFile, params)

def usage():
    print("shelfspace.py parameters")
    print(" -h             view this listing of parameters")
    print(" --help         view this listing of parameters")
    print(" -i srcfile     use srcfile as the input image")
    print(" -s             use sharpen filter on input image")
    print(" -b bounds      comma-separated list of coordinates for bounding polygon (4-sided)")
    print(" --arcmin val   minimum arc length for detected polygons")
    print(" --arcmax val   maximum arc length for detected polygons")
    print(" --areamin val  minimum triangle area for filtering detected triangles")
    print(" --areamax val  maximum triangle area for filtering detected triangles")
    print(" --paf val      polygon approximation factor for converting detected contours to polygons")
    print(" --legmin val   minimum leg length for triangle filtering")
    print(" --legmax val   maximum leg length for triangle filtering")
    print(" --legvar val   maximum difference in triangle leg length")
    print(" --nothresh     disable adaptive threshold step")
    print(" --thresh val   perform manual threshold at specified value")
    print(" -p             display default parameter values")
    print(" --state        output internal state images (state_01 through state_10)")
    print(" --expected     expected number of triangles detectable in empty shelf")
    print(" --undistort coeffs   apply undistort filter to image (coeffs is list of 4 parameters)")
    print(" --equhist      equalize input image histogram")


# call main function
if __name__ == "__main__":
    main(sys.argv[1:])
