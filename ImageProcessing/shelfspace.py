import cv2
import sys
import getopt
import json
import numpy as np
import math

# main program entry point - decode parameters, act accordingly
def main(argv):
    # set default values
    srcImageFile=''
    useBounds = False
    useSharpen = False
    outputState = False
    useThreshold = True
    useDistort = False
    useStaticThreshold = False
    equalizeHist = False
    minArcLength = 80
    maxArcLength = 30000
    minArea = 500
    maxArea = 50000
    polyApproxFactor = 3.5
    minLegLength = 10
    maxLegLength = 100
    maxLegVar = 100
    baseTriangleCount = 252
    staticThreshold = 128
    bounds = []
    distortCoeffs = np.zeros((4,1),np.float64)

    # attempt to parse commandline parameters
    try:
        opts, args = getopt.getopt(argv, "hi:b:ps", ["help","arcmin=","arcmax=","areamin=","areamax=","paf=","state","nothresh","legmin=","legmax=","legvar=","expected=","undistort=","thresh=","equhist"])
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
            print("Minimum arc length: " + str(minArcLength))
            print("Maximum arc length: " + str(maxArcLength))
            print("Minimum triangle area: " + str(minArea))
            print("Maximum triangle area: " + str(maxArea))
            print("Polygon Approximation Factor: " + str(polyApproxFactor))
            print("Minimum leg length: " + str(minLegLength))
            print("Maximum leg length: " + str(maxLegLength))
            print("Maximum leg variation: " + str(maxLegVar))
            print("Expected triangle count: " + str(baseTriangleCount))
            sys.exit()
        elif opt == '-i':
            srcImageFile = arg
        elif opt == '-b':
            strBounds = arg
            useBounds = True
            splitBounds = strBounds.split(",")
            if len(splitBounds) != 8:
                print("Invalid boundary coordinates")
                usage()
                sys.exit(2)
            for i in range(0,4):
                coord = [int(splitBounds[i*2]),int(splitBounds[i*2+1])]
                bounds.append(coord)
            bounds = np.array([bounds], np.int32)
            #print(bounds)
        elif opt == '--undistort':
            strDistort = arg
            useDistort = True
            splitDistort = strDistort.split(",")
            if len(splitDistort) != 4:
              print("Invalid undistort coefficients")
              usage()
              sys.exit(2)
            for i in range(0,4):
              coeff = float(splitDistort[i])
              distortCoeffs[i,0] = coeff
        elif opt == '-s':
            useSharpen = True
        elif opt == '--arcmin':
            minArcLength = int(arg)
        elif opt == '--arcmax':
            maxArcLength = int(arg)
        elif opt == '--areamin':
            minArea = int(arg)
        elif opt == '--areamax':
            maxArea = int(arg)
        elif opt == '--legmin':
            minLegLength = int(arg)
        elif opt == '--legmax':
            maxLegLength = int(arg)
        elif opt == '--legvar':
            maxLegVar = int(arg)
        elif opt == '--paf':
            polyApproxFactor = float(arg)
        elif opt == '--state':
            outputState = True
        elif opt == '--nothresh':
            useThreshold = False
        elif opt == '--thresh':
            useStaticThreshold = True
            staticThreshold = int(arg)
        elif opt == '--expected':
            baseTriangleCount = int(arg)
        elif opt == '--equhist':
            equalizeHist = True

    if srcImageFile == '':
        usage()
        sys.exit(2)
        
    # read source
    image = readSourceImage(srcImageFile, outputState, useSharpen, useThreshold, useDistort, distortCoeffs, useStaticThreshold, staticThreshold,equalizeHist)

    # undistort image
    #if useDistort == True:
    #  image = undistortImage(image, distortCoeffs, outputState)

    # detect triangles
    contourCount, rawTriCount, boundCount, arcCount, areaCount, finalCount, tris = findTriangles(image, minArcLength, maxArcLength, minArea, maxArea, polyApproxFactor, useBounds, bounds, outputState, minLegLength, maxLegLength, maxLegVar)

    fullPercent = 1.0 - float(finalCount)/float(baseTriangleCount)

    # build output dictionary
    if bounds.size > 0:
        bounds = bounds.tolist()

    #if distortCoeffs != []:
    distortCoeffs = distortCoeffs.flatten()
    distortCoeffs = distortCoeffs.tolist()

    imgheight, imgwidth = image.shape[:2]

    outDict = {'Parameters':{
                  'TrianglesExpected':baseTriangleCount,
                  'MinArcLength':minArcLength,
                  'MaxArcLength':maxArcLength,
                  'MinTriangleArea':minArea,
                  'MaxTriangleArea':maxArea,
                  'MinLegLength':minLegLength,
                  'MaxLegLength':maxLegLength,
                  'MaxLegVariation':maxLegVar,
                  'PolygonApproximationFactor':polyApproxFactor,
                  'UseAdaptiveThreshold':useThreshold,
                  'SharpenImage':useSharpen,
                  'UseBoundingPolygon':str(useBounds),
                  'BoundingPolygon':bounds,
                  'UndistortImage':str(useDistort),
                  'UndistortCoeffs':distortCoeffs,
                  'UseStaticThreshold':useStaticThreshold,
                  'StaticThreshold':staticThreshold,
                  'EqualizeHistogram':str(equalizeHist)},
               'DetectionDetails':{
                  'ContourCount':contourCount, 
                  'RawTriangleCount':rawTriCount,
                  'InBoundingPolyCount':boundCount,
                  'CorrectArclenTriangleCount':arcCount, 
                  'CorrectAreaTriangleCount':areaCount,
                  'ImageWidth':imgwidth,
                  'ImageHeight':imgheight,
                  'TriangleCoords':tris},
               'TriangleCount':finalCount,
               'PercentFull':fullPercent}

    # write output JSON to STDOUT
    json.dump(outDict, sys.stdout)
    #sys.stdout.write(str(outDict))

def readSourceImage(s,outputState,useSharpen,useThreshold,useDistort,distortCoeffs,useStaticThreshold,staticThreshold,equalizeHist):
    # read input file
    img = cv2.imread(s)
    # write state image
    if outputState == True:
      cv2.imwrite('state_01_input.jpg', img)

    if useDistort == True:
      img = undistortImage(img, distortCoeffs, outputState)

    # sharpen
    if useSharpen == True:
      kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
      img = cv2.filter2D(img, -1, kernel)
      # write state image
      if outputState == True:
        cv2.imwrite('state_03_sharpen.jpg',img)

    # convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # write state image
    if outputState == True:
      cv2.imwrite('state_04_grayscale.jpg', img)

    #equalize histogram
    if equalizeHist == True:
      img = cv2.equalizeHist(img)
      # write state image
      if outputState == True:
        cv2.imwrite('state_05_histogramequalization.jpg', img)

    # apply adaptive threshold to image
    if useThreshold == True:
      img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 15)
      # write state image
      if outputState == True:
        cv2.imwrite('state_06_adaptivethreshold.jpg', img)

    # apply static threshold to image
    if useStaticThreshold == True:
      _, img = cv2.threshold(img, staticThreshold, 255, cv2.THRESH_BINARY)
      # write state image
      if outputState == True:
        cv2.imwrite('state_07_staticthreshold.jpg', img)

    return img    

def undistortImage(img, coeffs, outputState):
    camMatrix = np.eye(3, dtype=np.float32)
    
    camMatrix[0,2] = img.shape[1]/2.0 #width
    camMatrix[1,2] = img.shape[0]/2.0 #height
    camMatrix[0,0] = 10.0
    camMatrix[1,1] = 10.0

    img = cv2.undistort(img, camMatrix, coeffs)

    # write state image
    if outputState == True:
      cv2.imwrite('state_02_undistort.jpg', img)

    return img

def checkBounds(shape, usebounds, bounds):
    if usebounds == False:
        return True

    for pt in shape:
        if cv2.pointPolygonTest(bounds, (pt[0][0],pt[0][1]), False) < 1:
            return False

    return True

def segLen(x1, y1, x2, y2):
    deltax = x2-x1
    deltay = y2-y1
    return int(math.sqrt(deltax * deltax + deltay * deltay))

def findTriangles(img, minArc, maxArc, minArea, maxArea, PAF, UseBounds, BoundPoly, outputState, minLegLength, maxLegLength, maxLegVar):
    rawContourCount = 0
    rawTriCount = 0
    boundTriCount = 0
    arclenTriCount = 0
    areaTriCount = 0
    legLengthTriCount = 0
    legVarTriCount = 0
    finalTriCount = 0
    triList = []
    #triList = {}
    stateColor=(0,255,0)
    stateBoundColor=(0,0,255)
    stateLineWidth = 4

    if outputState == True:
      imgOutput = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
      imgBounds = imgOutput.copy()
      if UseBounds == True:
        cv2.line(imgBounds, (BoundPoly[0][0][0],BoundPoly[0][0][1]),(BoundPoly[0][1][0],BoundPoly[0][1][1]),stateBoundColor,stateLineWidth)
        cv2.line(imgBounds, (BoundPoly[0][1][0],BoundPoly[0][1][1]),(BoundPoly[0][2][0],BoundPoly[0][2][1]),stateBoundColor,stateLineWidth)
        cv2.line(imgBounds, (BoundPoly[0][2][0],BoundPoly[0][2][1]),(BoundPoly[0][3][0],BoundPoly[0][3][1]),stateBoundColor,stateLineWidth)
        cv2.line(imgBounds, (BoundPoly[0][3][0],BoundPoly[0][3][1]),(BoundPoly[0][0][0],BoundPoly[0][0][1]),stateBoundColor,stateLineWidth)

      imgContours = imgOutput.copy()
      imgPAF = imgOutput.copy()
      imgRawTris = imgOutput.copy()
      imgBoundedTris = imgBounds.copy()
      imgArcLen = imgOutput.copy()
      imgArea = imgOutput.copy()
      imgLegLength = imgOutput.copy()
      imgLegVar = imgOutput.copy()

    _, contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    if outputState == True:
      cv2.drawContours(imgContours, contours, -1, stateColor, stateLineWidth)

    for i in range(0, len(contours)):
        rawContourCount += 1
        shape = cv2.approxPolyDP(contours[i], PAF, True)

        if outputState == True:
          outShape=[shape]
          cv2.drawContours(imgPAF, outShape, -1, stateColor, stateLineWidth)

        if len(shape) == 3:
            if outputState == True:
              cv2.line(imgRawTris, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
              cv2.line(imgRawTris, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
              cv2.line(imgRawTris, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

            rawTriCount += 1
            if checkBounds(shape, UseBounds, BoundPoly) == True:
                boundTriCount += 1

                if outputState == True:
                  cv2.line(imgBoundedTris, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
                  cv2.line(imgBoundedTris, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
                  cv2.line(imgBoundedTris, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

                arcLength = cv2.arcLength(shape, True)
    
                if arcLength > minArc and arcLength < maxArc:
                    arclenTriCount += 1

                    if outputState == True:
                      cv2.line(imgArcLen, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
                      cv2.line(imgArcLen, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
                      cv2.line(imgArcLen, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

                    area = cv2.contourArea(shape)

                    if area > minArea and area < maxArea:
                        #finalTriCount += 1
                        areaTriCount += 1
                        #triName="tri" + str(finalTriCount)
                        #triList[triName]={"x1":int(shape[0][0][0]),"y1":shape[0][0][1],"x2":shape[1][0][0],"y2":shape[1][0][1],"x3":shape[2][0][0],"y3":shape[2][0][1]}

                        if outputState == True:
                          cv2.line(imgArea, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
                          cv2.line(imgArea, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
                          cv2.line(imgArea, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

                        leglen1 = segLen(shape[0][0][0],shape[0][0][1],shape[1][0][0],shape[1][0][1])
                        leglen2 = segLen(shape[1][0][0],shape[1][0][1],shape[2][0][0],shape[2][0][1])
                        leglen3 = segLen(shape[2][0][0],shape[2][0][1],shape[0][0][0],shape[0][0][1])
	
                        if (leglen1 > minLegLength and leglen2 > minLegLength and leglen3 > minLegLength) and (leglen1 < maxLegLength and leglen2 < maxLegLength and leglen3 < maxLegLength):
                          legLengthTriCount += 1
                          #finalTriCount += 1

                          if outputState == True:
                            cv2.line(imgLegLength, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
                            cv2.line(imgLegLength, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
                            cv2.line(imgLegLength, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

                          if abs(leglen1 - leglen2) < maxLegVar and abs(leglen2-leglen3) < maxLegVar and abs(leglen1-leglen3) < maxLegVar:
                            legVarTriCount += 1
                            finalTriCount += 1

                            triList.append([[int(shape[0][0][0]),int(shape[0][0][1])],[int(shape[1][0][0]),int(shape[1][0][1])],[int(shape[2][0][0]),int(shape[2][0][1])]])
 
                            if outputState == True:
                              cv2.line(imgLegVar, (shape[0][0][0],shape[0][0][1]),(shape[1][0][0],shape[1][0][1]),stateColor,stateLineWidth)
                              cv2.line(imgLegVar, (shape[1][0][0],shape[1][0][1]),(shape[2][0][0],shape[2][0][1]),stateColor,stateLineWidth)
                              cv2.line(imgLegVar, (shape[2][0][0],shape[2][0][1]),(shape[0][0][0],shape[0][0][1]),stateColor,stateLineWidth)

    # write state images
    if outputState == True:
      cv2.imwrite('state_08_detectedcontours.jpg',imgContours)
      cv2.imwrite('state_09_polyapproxfactor.jpg',imgPAF)
      cv2.imwrite('state_10_rawtriangles.jpg',imgRawTris)
      cv2.imwrite('state_11_boundedtriangles.jpg',imgBoundedTris)
      cv2.imwrite('state_12_arclength.jpg',imgArcLen)
      cv2.imwrite('state_13_area.jpg',imgArea)
      cv2.imwrite('state_14_leglength.jpg',imgLegLength)
      cv2.imwrite('state_15_legvar.jpg',imgLegVar)

    return (rawContourCount, rawTriCount, boundTriCount, arclenTriCount, areaTriCount, finalTriCount, triList)

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

