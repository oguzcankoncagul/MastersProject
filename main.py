import sys, shutil, os, time
from ASTTraversal import *
from BitmapProcessing import *
from TestCircuitGeneration import *
from FileManagement import *
from time import gmtime, strftime

#Main method

#Variables and run configuration
TotalBitmapQuantity = 100
ComponentQuantity = 25
BMPWidth, BMPHeight, BMPDepth = (32*ComponentQuantity) , 80, 7
doConsoleOutput = False
clang.cindex.Config.set_library_path("D:/LLVM/bin")

#Folder locations
legUpInstallDirectory = "D:\LegUp-5.1"
mainLegUpFolder = "D:\LegUp-5.1\workspace\MastersProjectLegUp"
scriptFolder = 'D:\PycharmProjects\MastersProject'
bmpFolder = 'D:\Computer Science\Masters Project\Bitmaps'

#Clean up previous files from folders
cleanAllFolders(mainLegUpFolder,bmpFolder)

for bmpNo in range(TotalBitmapQuantity):
    #Delete previous test circuit file from working directory (still documented elsewhere)
    cleanFolder(mainLegUpFolder, ".c")
    cleanFolder((mainLegUpFolder + "/Hardware"), ".c")
    cleanFolder((mainLegUpFolder + "/Hardware/reports"), ".rpt")

    #Auto generate test circuit
    timestamp = strftime("%m%d%H%M%S", gmtime())
    generateTestCircuit(ComponentQuantity, timestamp, mainLegUpFolder, bmpFolder)

    #Get resource estimates
    luts, registers = getLegUpEstimates(timestamp, mainLegUpFolder,legUpInstallDirectory)
    resourceEstimates = [luts, registers]

    #Producing and fetching AST file
    fetchAST(timestamp, mainLegUpFolder, scriptFolder)

    #Initial setup
    tu = setupParser('test' +timestamp +'.ast')
    BMPArray = initialiseBMPArray(BMPWidth, BMPHeight, BMPDepth)
    rootNode = tu.cursor

    #Parse AST and determine tree structure
    traverseAST(BMPArray, rootNode, 0)

    #Bitmap processing
    BMPargs = [BMPArray, BMPHeight, BMPWidth]
    enumNodes(*BMPargs)

    #Bitmap parameter initialisations
    encodeOtherRE = False
    labelChoice = 0
    doComposites = False
    doFill = False
    datasetNo = 1

    #Generate all bitmap variations modelling the test circuit
    print('Generating bitmaps...(' + str(bmpNo + 1) + '/' + str(TotalBitmapQuantity) + ')')
    for encodeOtherRE in [False, True]:
        for labelChoice in [0,1]:
            for doComposites in [False,True]:
                for doFill in [False,True]:
                    labelRE = resourceEstimates[labelChoice]
                    if labelChoice == 0:
                        dataRE = resourceEstimates[0]
                    elif labelChoice == 1:
                        dataRE = resourceEstimates[1]
                    bmpParameters = [encodeOtherRE, doFill, doComposites]
                    createImage(*BMPargs, *bmpParameters, timestamp, labelRE, dataRE, datasetNo, bmpFolder)
                    datasetNo += 1

    #Console output
    if (doConsoleOutput == True):
        for i in range(BMPHeight):
            print(BMPArray[i][:][:])

#Post-op clean-up
cleanFolder(scriptFolder, '.ast')

