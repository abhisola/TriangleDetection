#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import sys
import getopt
import json
import numpy as np
import math

class TriRecognizeParams:
    def __init__(self):
        self.useBounds = False
        self.useSharpen = False
        self.outputState = False
        self.useThreshold = True
        self.useDistort = False
        self.useStaticThreshold = False
        self.equalizeHist = False
        self.minArcLength = 80
        self.maxArcLength = 30000
        self.minArea = 500
        self.maxArea = 50000
        self.polyApproxFactor = 3.5
        self.minLegLength = 10
        self.maxLegLength = 100
        self.maxLegVar = 100
        self.baseTriangleCount = 252
        self.staticThreshold = 128
        self.bounds = []
        self.distortCoeffs = np.zeros((8, 1), np.float64)


class TriRecognizer:
    @staticmethod
    def processImage(srcImageFile, params):
        # read source
        image = TriRecognizer.readSourceImage(srcImageFile, params)

        # detect triangles
        contourCount, rawTriCount, boundCount, arcCount, areaCount, finalCount, tris = TriRecognizer.findTriangles(image, params)

        fullPercent = 1.0 - float(finalCount) / float(params.baseTriangleCount)

        # build output dictionary
        bounds = []
        if len(params.bounds) > 0:
            bounds = params.bounds.tolist()

        # if distortCoeffs != []:
        distortCoeffs = params.distortCoeffs.flatten()
        distortCoeffs = params.distortCoeffs.tolist()

        imgheight, imgwidth = image.shape[:2]

        outDict = {'Parameters': {
            'TrianglesExpected': params.baseTriangleCount,
            'MinArcLength': params.minArcLength,
            'MaxArcLength': params.maxArcLength,
            'MinTriangleArea': params.minArea,
            'MaxTriangleArea': params.maxArea,
            'MinLegLength': params.minLegLength,
            'MaxLegLength': params.maxLegLength,
            'MaxLegVariation': params.maxLegVar,
            'PolygonApproximationFactor': params.polyApproxFactor,
            'UseAdaptiveThreshold': params.useThreshold,
            'SharpenImage': params.useSharpen,
            'UseBoundingPolygon': str(params.useBounds),
            'BoundingPolygon': bounds,
            'UndistortImage': str(params.useDistort),
            'UndistortCoeffs': distortCoeffs,
            'UseStaticThreshold': params.useStaticThreshold,
            'StaticThreshold': params.staticThreshold,
            'EqualizeHistogram': str(params.equalizeHist)},
            'DetectionDetails': {
                'ContourCount': contourCount,
                'RawTriangleCount': rawTriCount,
                'InBoundingPolyCount': boundCount,
                'CorrectArclenTriangleCount': arcCount,
                'CorrectAreaTriangleCount': areaCount,
                'ImageWidth': imgwidth,
                'ImageHeight': imgheight,
                'TriangleCoords': tris
            },
            'TriangleCount': finalCount,
            'PercentFull': fullPercent}

        # write output JSON to STDOUT
        # json.dump(outDict, sys.stdout, indent=4)
        json.dump(outDict, sys.stdout)
        # sys.stdout.write(str('\nTrangles Count: '+str(outDict['TriangleCount'])+'\nPercent: '+str(outDict['PercentFull'])))
        # sys.stdout.write(str(outDict))

    @staticmethod
    def readSourceImage(s, params):
        # read input file
        img = cv2.imread(s)
        # write state image
        if params.outputState == True:
            cv2.imwrite('state_01_input.jpg', img)

        if params.useDistort == True:
            img = TriRecognizer.__undistortImage(img, params.distortCoeffs, params.outputState)

        # sharpen
        if params.useSharpen == True:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            img = cv2.filter2D(img, -1, kernel)
            # write state image
            if params.outputState == True:
                cv2.imwrite('state_03_sharpen.jpg', img)

        # convert to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # write state image
        if params.outputState == True:
            cv2.imwrite('state_04_grayscale.jpg', img)

        # equalize histogram
        if params.equalizeHist == True:
            img = cv2.equalizeHist(img)
            # write state image
            if params.outputState == True:
                cv2.imwrite('state_05_histogramequalization.jpg', img)

        # apply adaptive threshold to image
        if params.useThreshold == True:
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 15)
            # write state image
            if params.outputState == True:
                cv2.imwrite('state_06_adaptivethreshold.jpg', img)

        # apply static threshold to image
        if params.useStaticThreshold == True:
            _, img = cv2.threshold(img, staticThreshold, 255, cv2.THRESH_BINARY)
            # write state image
            if params.outputState == True:
                cv2.imwrite('state_07_staticthreshold.jpg', img)

        return img

    @staticmethod
    def __undistortImage(img, coeffs, outputState):
        camMatrix = np.eye(3, dtype=np.float32)

        w = img.shape[1]
        h = img.shape[0]
        camMatrix[0, 2] = img.shape[1] / 2.0  # width
        camMatrix[1, 2] = img.shape[0] / 2.0  # height
        camMatrix[0, 0] = 10.0
        camMatrix[1, 1] = 10.0

        dim = (w, h)
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camMatrix, coeffs, dim, 1, dim)
        mapx, mapy = cv2.initUndistortRectifyMap(camMatrix, coeffs, None, newcameramtx, dim, 5)
        img = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

        # write state image
        if outputState == True:
            cv2.imwrite('state_02_undistort.jpg', img)

        return img

    @staticmethod
    def __checkBounds(shape, usebounds, bounds):
        if usebounds == False:
            return True

        for pt in shape:
            if cv2.pointPolygonTest(bounds, (pt[0][0], pt[0][1]), False) < 1:
                return False

        return True

    @staticmethod
    def __segLen(x1, y1, x2, y2):
        deltax = x2 - x1
        deltay = y2 - y1
        return int(math.sqrt(deltax * deltax + deltay * deltay))

    @staticmethod
    def __drawTriangle(img, shape, color=(0, 255, 0), lineWidth=4):
        cv2.line(img, (shape[0][0][0], shape[0][0][1]), (shape[1][0][0], shape[1][0][1]), color, lineWidth)
        cv2.line(img, (shape[1][0][0], shape[1][0][1]), (shape[2][0][0], shape[2][0][1]), color, lineWidth)
        cv2.line(img, (shape[2][0][0], shape[2][0][1]), (shape[0][0][0], shape[0][0][1]), color, lineWidth)

    @staticmethod
    def findTriangles(img, params):
        rawContourCount = 0
        rawTriCount = 0
        boundTriCount = 0
        arclenTriCount = 0
        areaTriCount = 0
        legLengthTriCount = 0
        legVarTriCount = 0
        finalTriCount = 0
        triList = []
        tmpTriList = []
        stateColor = (0, 255, 0)
        stateBoundColor = (0, 0, 255)
        stateLineWidth = 4

        if params.outputState == True:
            imgOutput = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            imgBounds = imgOutput.copy()
            if params.useBounds == True:
                cv2.line(imgBounds, (params.bounds[0][0][0], params.bounds[0][0][1]),
                         (params.bounds[0][1][0], params.bounds[0][1][1]),
                         stateBoundColor, stateLineWidth)
                cv2.line(imgBounds, (params.bounds[0][1][0], params.bounds[0][1][1]),
                         (params.bounds[0][2][0], params.bounds[0][2][1]),
                         stateBoundColor, stateLineWidth)
                cv2.line(imgBounds, (params.bounds[0][2][0], params.bounds[0][2][1]),
                         (params.bounds[0][3][0], params.bounds[0][3][1]),
                         stateBoundColor, stateLineWidth)
                cv2.line(imgBounds, (params.bounds[0][3][0], params.bounds[0][3][1]),
                         (params.bounds[0][0][0], params.bounds[0][0][1]),
                         stateBoundColor, stateLineWidth)

            imgContours = imgOutput.copy()
            imgPAF = imgOutput.copy()
            imgRawTris = imgOutput.copy()
            imgBoundedTris = imgBounds.copy()
            imgArcLen = imgOutput.copy()
            imgArea = imgOutput.copy()
            imgLegLength = imgOutput.copy()
            imgLegVar = imgOutput.copy()
            imgCrossTris = imgOutput.copy()

        _, contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if params.outputState == True:
            cv2.drawContours(imgContours, contours, -1, stateColor, stateLineWidth)

        for i in range(0, len(contours)):
            rawContourCount += 1
            shape = cv2.approxPolyDP(contours[i], params.polyApproxFactor, True)

            if params.outputState == True:
                outShape = [shape]
                cv2.drawContours(imgPAF, outShape, -1, stateColor, stateLineWidth)

            if len(shape) == 3:
                if params.outputState == True:
                    TriRecognizer.__drawTriangle(imgRawTris, shape, stateColor, stateLineWidth)

                rawTriCount += 1
                if TriRecognizer.__checkBounds(shape, params.useBounds, params.bounds) == True:
                    boundTriCount += 1

                    if params.outputState == True:
                        TriRecognizer.__drawTriangle(imgBoundedTris, shape, stateColor, stateLineWidth)

                    arcLength = cv2.arcLength(shape, True)

                    if arcLength > params.minArcLength and arcLength < params.maxArcLength:
                        arclenTriCount += 1

                        if params.outputState == True:
                            TriRecognizer.__drawTriangle(imgArcLen, shape, stateColor, stateLineWidth)

                        area = cv2.contourArea(shape)

                        if area > params.minArea and area < params.maxArea:
                            # finalTriCount += 1
                            areaTriCount += 1
                            # triName="tri" + str(finalTriCount)
                            # triList[triName]={"x1":int(shape[0][0][0]),"y1":shape[0][0][1],"x2":shape[1][0][0],"y2":shape[1][0][1],"x3":shape[2][0][0],"y3":shape[2][0][1]}

                            if params.outputState == True:
                                TriRecognizer.__drawTriangle(imgArea, shape, stateColor, stateLineWidth)

                            leglen1 = TriRecognizer.__segLen(shape[0][0][0], shape[0][0][1], shape[1][0][0], shape[1][0][1])
                            leglen2 = TriRecognizer.__segLen(shape[1][0][0], shape[1][0][1], shape[2][0][0], shape[2][0][1])
                            leglen3 = TriRecognizer.__segLen(shape[2][0][0], shape[2][0][1], shape[0][0][0], shape[0][0][1])

                            if (leglen1 > params.minLegLength and leglen2 > params.minLegLength and leglen3 > params.minLegLength) and \
                                    (leglen1 < params.maxLegLength and leglen2 < params.maxLegLength and leglen3 <params. maxLegLength):
                                legLengthTriCount += 1

                                if params.outputState == True:
                                    TriRecognizer.__drawTriangle(imgLegLength, shape, stateColor, stateLineWidth)

                                if abs(leglen1 - leglen2) < params.maxLegVar and \
                                        abs(leglen2 - leglen3) < params.maxLegVar and \
                                        abs(leglen1 - leglen3) < params.maxLegVar:
                                    legVarTriCount += 1
                                    tmpTriList.append(shape)

                                    if params.outputState == True:
                                        TriRecognizer.__drawTriangle(imgLegVar, shape, stateColor, stateLineWidth)

        # remove crossed or internal triangles
        tmpTriList = np.array(tmpTriList, np.int32)
        for shape in tmpTriList:
            cross = False
            for bound in tmpTriList:
                if TriRecognizer.__checkBounds(shape, True, bound):
                    cross = True
                    break;

            if not cross:
                finalTriCount += 1
                triList.append([[int(shape[0][0][0]), int(shape[0][0][1])],
                                [int(shape[1][0][0]), int(shape[1][0][1])],
                                [int(shape[2][0][0]), int(shape[2][0][1])]])

                if params.outputState == True:
                    TriRecognizer.__drawTriangle(imgCrossTris, shape, stateColor, stateLineWidth)

        # write state images
        if params.outputState == True:
            cv2.imwrite('state_08_detectedcontours.jpg', imgContours)
            cv2.imwrite('state_09_polyapproxfactor.jpg', imgPAF)
            cv2.imwrite('state_10_rawtriangles.jpg', imgRawTris)
            cv2.imwrite('state_11_boundedtriangles.jpg', imgBoundedTris)
            cv2.imwrite('state_12_arclength.jpg', imgArcLen)
            cv2.imwrite('state_13_area.jpg', imgArea)
            cv2.imwrite('state_14_leglength.jpg', imgLegLength)
            cv2.imwrite('state_15_legvar.jpg', imgLegVar)
            cv2.imwrite('state_16_cross.jpg', imgCrossTris)

        return (rawContourCount, rawTriCount, boundTriCount, arclenTriCount, areaTriCount, finalTriCount, triList)
