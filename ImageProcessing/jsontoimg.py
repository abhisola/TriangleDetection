import cv2
import sys
import getopt
import json

# main program
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help"])
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
        elif opt == "-i":
            srcImgFile = arg
#        elif opt == "-j":
#            srcJSONFile = arg
        elif opt == "-o":
            destImgFile = arg

    # read source
    srcImg = readSourceImage(srcImgFile)

    # read JSON
    parsedData = parseJSON()

    # apply JSON data to image
    image = applyParsedJSON(srcImg, parsedData)

    # write output
    writeDestImage(image, destImgFile)

def readSourceImage(s):
    img = cv2.imread(s)
    return img

def writeDestImage(img, s):
    cv2.imwrite(s, img)

def parseJSON():
    res = json.load(sys.stdin)
#    print(res)
    return res

def applyParsedJSON(img, data):
    # draw bounding poly
    if data['Parameters']['UseBoundingPolygon'] == True:
        boundPoly = data['Parameters']['BoundingPolygon'][0]

        cv2.line(img, (boundPoly[0][0],boundPoly[0][1]),(boundPoly[1][0],boundPoly[1][1]),(0,0,255),2)
        cv2.line(img, (boundPoly[1][0],boundPoly[1][1]),(boundPoly[2][0],boundPoly[2][1]),(0,0,255),2)
        cv2.line(img, (boundPoly[2][0],boundPoly[2][1]),(boundPoly[3][0],boundPoly[3][1]),(0,0,255),2)
        cv2.line(img, (boundPoly[3][0],boundPoly[3][1]),(boundPoly[0][0],boundPoly[0][1]),(0,0,255),2)

        #print(boundPoly)

    # draw triangles
    triCoords = data['DetectionDetails']['TriangleCoords']

    #print(triCoords)
    for tri in triCoords:
        #print(tri)
        cv2.line(img, (tri[0][0],tri[0][1]),(tri[1][0],tri[1][1]),(0,255,0),2)
        cv2.line(img, (tri[1][0],tri[1][1]),(tri[2][0],tri[2][1]),(0,255,0),2)
        cv2.line(img, (tri[2][0],tri[2][1]),(tri[0][0],tri[0][1]),(0,255,0),2)

    return img

def usage():
    print("Program options")
    print("  -h       view this list of options")
    print("  --help   view this list of options")
    print("  -i file  use file as input image")
#    print("  -j file  use file as input JSON")
    print("  -o file  use file as output image")


# call main program
if __name__ == "__main__":
    main(sys.argv[1:])

