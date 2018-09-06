from PIL import Image
import math, os

def createImage(BMPArrayOriginal, BMPHeight, BMPWidth, encodeOtherRE, doFill, doComposites, timestamp, labelRE, dataRE, datasetNo, bmpFolder):

    #Correct bitmap size
    if (doComposites == False):
        BMPHeight = 20

    #To conserve the original data
    BMPArrayTemp = initialiseBMPArray(BMPWidth,BMPHeight,7)
    for i in range(BMPHeight):
        for j in range(BMPWidth):
            BMPArrayTemp[i][j][:] = BMPArrayOriginal[i][j][:]
    if (doFill == True):
        fillArray(BMPArrayTemp, BMPHeight, BMPWidth, 7)

    #Create image template
    if (encodeOtherRE == True):
        img = Image.new('RGBA', (BMPWidth, BMPHeight), "white")
    else:
        img = Image.new('RGB', (BMPWidth, BMPHeight), "white")
    pixels = img.load()

    for i in range(0,BMPWidth):
        for j in range(0,BMPHeight):
            def RedData(minusOffset):
                return int(BMPArrayTemp[j+minusOffset][i][2]/5)
            def GreenData(minusOffset):
                return BMPArrayTemp[j+minusOffset][i][4]*7
            def BlueData(minusOffset):
                return BMPArrayTemp[j+minusOffset][i][6]
            def LabelData():
                return int(dataRE * (255/9000))

            if (encodeOtherRE == True):
                if j < 21:
                    pixels[i, j] = (RedData(0), GreenData(0), BlueData(0), LabelData())
                elif j < 41 and j > 20:
                    pixels[i, j] = (0, int((RedData(-20) + BlueData(-20)) / 2), 0, LabelData())
                elif j < 61 and j > 40:
                    pixels[i, j] = (int((BlueData(-40) + GreenData(-40)) / 2), 0, 0, LabelData())
                elif j < 81 and j > 60:
                    pixels[i, j] = (0, 0, int((RedData(-60) + GreenData(-60)) / 2), LabelData())
            else:
                if j < 21:
                    pixels[i, j] = (RedData(0), GreenData(0), BlueData(0))
                elif j < 41 and j > 20:
                    pixels[i, j] = (0, int((RedData(-20) + BlueData(-20)) / 2), 0)
                elif j < 61 and j > 40:
                    pixels[i, j] = (int((BlueData(-40) + GreenData(-40)) / 2), 0, 0)
                elif j < 81 and j > 60:
                    pixels[i, j] = (0, 0, int((RedData(-60) + GreenData(-60)) / 2))

    #Calculate a class label for the test circuit
    labelClass1 = math.floor(labelRE/100)
    labelClass3 = math.floor(labelRE/300)
    labelClass5 = math.floor(labelRE/500)
    labelClass10 = math.floor(labelRE/1000)

    #Save output bitmaps to appropriate dataset folder & bin
    if not os.path.exists(bmpFolder + '/BMP1/Dataset' + str(datasetNo) + "/"+ str(labelClass1)):
        os.makedirs(bmpFolder + '/BMP1/Dataset' + str(datasetNo) + "/"+ str(labelClass1))
    img.save(bmpFolder + '/BMP1/Dataset' + str(datasetNo) + "/"+ str(labelClass1) + "/bmp"+ timestamp + str(datasetNo)+ '.png')

    if not os.path.exists(bmpFolder + '/BMP3/Dataset' + str(datasetNo) + "/"+ str(labelClass3)):
        os.makedirs(bmpFolder + '/BMP3/Dataset' + str(datasetNo) + "/"+ str(labelClass3))
    img.save(bmpFolder + '/BMP3/Dataset' + str(datasetNo) + "/"+ str(labelClass3) + "/bmp"+ timestamp + str(datasetNo)+ '.png')

    if not os.path.exists(bmpFolder + '/BMP5/Dataset' + str(datasetNo) + "/"+ str(labelClass5)):
        os.makedirs(bmpFolder + '/BMP5/Dataset' + str(datasetNo) + "/"+ str(labelClass5))
    img.save(bmpFolder + '/BMP5/Dataset' + str(datasetNo) + "/"+ str(labelClass5) + "/bmp"+ timestamp + str(datasetNo)+ '.png')

    if not os.path.exists(bmpFolder + '/BMP10/Dataset' + str(datasetNo) + "/"+ str(labelClass10)):
        os.makedirs(bmpFolder + '/BMP10/Dataset' + str(datasetNo) + "/"+ str(labelClass10))
    img.save(bmpFolder + '/BMP10/Dataset' + str(datasetNo) + "/"+ str(labelClass10) + "/bmp"+ timestamp + str(datasetNo)+ '.png')

def enumNodes(BMPArray, BMPHeight, BMPWidth):
    myDict = {}
    for i in range(BMPHeight):
        for j in range(BMPWidth):
            #Enumerate token kind
            tokenString = BMPArray[i][j][1]
            if tokenString in myDict and not (myDict[tokenString] is None):
                BMPArray[i][j][2] = myDict[tokenString]
            else:
                myDict[tokenString] = sum(bytearray(str(tokenString), 'utf-8'))
                BMPArray[i][j][2] = myDict[tokenString]

            #Enumerate data type (according to bitwidth)
            if str(BMPArray[i][j][3]) == ('INT' or 'VOLATILE INT'): #or 'POINTER'):
                BMPArray[i][j][4] = 32
            elif str(BMPArray[i][j][3]) == 'CHAR_S' :
                BMPArray[i][j][4] = 8
            else:
                BMPArray[i][j][4] = 0

            #Enumerate signal type
            if str(BMPArray[i][j][5]).startswith("mulMatrix"):
                BMPArray[i][j][6] = 250
            elif str(BMPArray[i][j][5]).startswith("DimArray" or "invMatrix"):
                BMPArray[i][j][6] = 220
            elif str(BMPArray[i][j][5]).startswith("sig"):
                BMPArray[i][j][6] = 180
            elif str(BMPArray[i][j][5]).startswith("tempRes"):
                BMPArray[i][j][6] = 150
            elif str(BMPArray[i][j][5]).startswith("mu"):
                BMPArray[i][j][6] = 130
            elif str(BMPArray[i][j][5]).startswith("inter" or "n" or "k"):
                BMPArray[i][j][6] = 80
            elif str(BMPArray[i][j][5]).startswith("select"):
                BMPArray[i][j][6] = 40
            elif str(BMPArray[i][j][5]).startswith("tempBit"):
                BMPArray[i][j][6] = 20
            else:
                BMPArray[i][j][6] = 0


def fillArray(BMPArrayTemp, BMPHeight, BMPWidth, BMPDepth):
    for i in range(BMPHeight):
        currentSample = [0] * BMPDepth
        for j in range(BMPWidth):
            if(BMPArrayTemp[i][j][0]) == True:
                currentSample = BMPArrayTemp[i][j][:]
                currentSample[0] = False
            else:
                BMPArrayTemp[i][j][:] = currentSample

def initialiseBMPArray(width, height, depth):
    return [[[0 for z in range(depth)] for x in range(width)] for y in range(height)]

