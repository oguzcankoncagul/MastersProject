import random, os, shutil, subprocess, time, binascii
from subprocess import Popen, PIPE
from FileManagement import *

# Multi-use variables
prev1dArray = [0]
prev2dArray = [0]
prev1dArray[0], prev2dArray[0] = 0, 0

def generateTestCircuit(ComponentQuantity, timestamp, mainLegUpFolder, bmpFolder):
    #Create text file to write code
    savePathTxt = bmpFolder + "\TXT/test" + timestamp + ".txt"
    testCircuit = open(savePathTxt, "w+")

    #GENERATE RANDOM TEST CIRCUIT

    #Include all header files in test circuit code
    with open(savePathTxt, "a") as myFile:
        for file in os.listdir(mainLegUpFolder + "\Repository\Headers"):
            if file.endswith(".h"):
                myFile.write("#include \"Repository/Headers/" + str(file) + "\"\n")
        myFile.write("const int EXIT_SUCCESS = 1;\nint main(){\n\tint i=0, j=0;\n\tvolatile int sig0=" + randomHexValue(4) +";\n\n")

    #Add random code snippets to test circuit
    prev2dArray[0],prev1dArray[0] = 0, 0
    for componentNo in range(ComponentQuantity):
        #Generate random number to choose function from library
        componentChoice = random.randint(1,11)
        addComponentCode(componentChoice, componentNo+1, savePathTxt)

    #Close off test circuit C code
    with open(savePathTxt, "a") as myFile:
        myFile.write("\treturn EXIT_SUCCESS;\n}")

    #----------------------------------------

    #Convert TXT to C file (test.c)
    shutil.copy2(savePathTxt,bmpFolder + "/test" + timestamp + ".c")
    shutil.copy2(savePathTxt, mainLegUpFolder + "/test.c")
    shutil.copy2(savePathTxt, mainLegUpFolder + "/Hardware/test.c")

def getLegUpEstimates(timestamp, mainLegUpFolder, legUpInstallDirectory):
    #Baby proofing
    if not os.path.exists(mainLegUpFolder + "/Hardware"):
        os.makedirs(mainLegUpFolder + "/Hardware")

    #Folder clean-up
    cygwinBash = Popen(( legUpInstallDirectory + "\cygwin64/bin/bash.exe"), stdin=PIPE, stdout=open(os.devnull, "w"),
                       stderr=subprocess.STDOUT)
    cygwinBash.stdin.write(b"cd /cygdrive/d/LegUp-5.1/workspace/MastersProjectLegUp/Hardware")
    cygwinBash.stdin.write(b"\n")
    cygwinBash.stdin.write(b"legup clean")
    cygwinBash.stdin.write(b"\n")

    # Call LegUp API/interface
    cygwinBash.stdin.write(b"legup fpga test.c")

    #Wait for Vivado output
    print("Calculating resource estimates...")
    cygwinBash.stdin.close()
    while not os.path.exists(mainLegUpFolder + "/Hardware/reports/summary.results.rpt"):
        time.sleep(1)

    #Extract relevant data from output file
    rptFile = mainLegUpFolder + "/Hardware/reports/summary.results.rpt"

    # Extract resource estimates from output
    lineNo = 1
    for line in open(rptFile):
        if line.startswith("| Slice LUTs      |") or line.startswith("| Slice Registers | "):
            words = line.split()
            if lineNo==1:
                luts = int(words[4])
                totalAvailableLUTs = int(words[8])
                lineNo +=1
            else:
                registers = int(words[4])
                totalAvailableRegisters = int(words[8])
                lineNo =1

    # Pass to BitMapProcessing method to add to matrix
    return luts, registers

def addComponentCode(componentChoice, componentNo, savePathTxt):

    # CASE STATEMENTS FOR EACH COMPONENT
    # SIGX FOR CONNECTION WHERE X IS COMPONENT NO+1

    def logicGate():
        def logicGateGen(opName, operator, notFlag):
            # Reset code snippet
            code = "\t//" + opName + "\n\tvolatile int sig" + str(componentNo) + "=0;\n"
            useMultipleSigs = random.randint(0, 1)
            # (Randomly) Extract 2 bits from the circuit
            if (useMultipleSigs == 1):
                code += "\tvolatile char tempBit" + str(2 * componentNo) + ";\n"
                code += "\ttempBit" + str(2 * componentNo) + "=(char)(sig" + str(
                    random.randint(1, max((componentNo - 1), 1))) + ">>" + str(
                    random.randint(1, 31)) + ")&0x01;\n"
                code += "\tvolatile char tempBit" + str(2 * componentNo + 1) + ";\n"
                code += "\ttempBit" + str(2 * componentNo + 1) + "=(char)(sig" + str(
                    random.randint(1, max((componentNo - 1), 1))) + ">>" + str(
                    random.randint(1, 31)) + ")&0x01;\n"
            else:
                prevSig = random.randint(1, max(componentNo - 1, 1))
                code += "\tchar tempBit" + str(2 * componentNo) + ";\n"
                code += "\ttempBit" + str(2 * componentNo) + "=(char)(sig" + str(prevSig) + ">>" + str(
                    random.randint(1, 31)) + ")&0x01;\n"
                code += "\tchar tempBit" + str(2 * componentNo + 1) + ";\n"
                code += "\ttempBit" + str(2 * componentNo + 1) + "=(char)(sig" + str(prevSig) + ">>" + str(
                    random.randint(1, 31)) + ")&0x01;\n"

            # Perform bitwise operation
            code += "\tchar tempRes" + str(componentNo) + ";\n"
            if (notFlag == False):
                code += "\ttempRes" + str(componentNo) + "=(char)(tempBit" + str(
                    2 * componentNo) + operator + "tempBit" + str(
                    2 * componentNo + 1) + ")&0x01;\n"
            elif (notFlag == True):
                code += "\ttempRes" + str(componentNo) + "=(char)(!((tempBit" + str(
                    2 * componentNo) + operator + "tempBit" + str(
                    2 * componentNo + 1) + ")&0x01));\n"

            # Insert result into random bit of input signal and output
            insertBit = random.randint(1, 31)
            code += "\tsig" + str(componentNo) + "=sig" + str(componentNo - 1) + ";\n"
            code += "\tsig" + str(componentNo) + " &= ~(1<<" + str(insertBit) + ");\n"
            code += "\tsig" + str(componentNo) + " |= (tempRes" + str(componentNo) + "<<" + str(insertBit) + ");\n"
            return code

        def andGate():
            opName, operator = "ANDGATE", "&"
            code = logicGateGen(opName, operator, False)
            return code

        def orGate():
            opName, operator = "ORGATE", "|"
            code = logicGateGen(opName, operator, False)
            return code

        def nandGate():
            opName, operator = "NANDGATE", "&"
            code = logicGateGen(opName, operator, True)
            return code

        def norGate():
            opName, operator = "NORGATE", "|"
            code = logicGateGen(opName, operator, True)
            return code

        def xorGate():
            opName, operator = "XORGATE", "^"
            code = logicGateGen(opName, operator, False)
            return code

        logicGates = {1: andGate,
                      2: orGate,
                      3: nandGate,
                      4: norGate,
                      5: xorGate}

        logicGateChoice = random.randint(1,5)
        logicGateCode = logicGates[logicGateChoice]()
        return logicGateCode

    def adder():
        #Reset code snippet
        code = "\t//ADDER\n\tint sig" + str(componentNo) + ";\n"

        #Generate random value arrays
        code += "\tint DimArray" + str(3*componentNo) + "[] = {" + randomHexValue(4)
        arraySize = random.randint(10, 18)
        prev1dArray[0] = 3*componentNo
        for element in range(arraySize):
            code += ","
            usePrevSig = random.randint(0, 1)
            if (usePrevSig == 1):
                code += "sig" + str(random.randint(0, componentNo - 1))
            else:
                code += randomHexValue(4)
        code += "};\n"
        #-------------------
        code += "\tint DimArray" + str((3*componentNo)+1) + "[] = {" + randomHexValue(4)
        for element in range(arraySize):
            code += ","
            usePrevSig = random.randint(0, 1)
            if (usePrevSig == 1):
                code += "sig" + str(random.randint(0, componentNo - 1))
            else:
                code += randomHexValue(4)
        code += "};\n"
        #--------------
        code += "\tint DimArray" + str((3 * componentNo)+2) + "[" + str(arraySize+1) + "] = {0};\n"
        code += "\tfor(i=0; i<" + str(arraySize+1) + ";i++){\n"
        code += "\t\tDimArray" + str((3*componentNo)+2) + "[i] = DimArray" + str(3*componentNo) + "[i] + DimArray" + str((3*componentNo)+1) + "[i];\n"
        code += "\t\tsig" + str(componentNo) + "= sig" + str(componentNo) + " + DimArray" + str((3*componentNo)+2) + "[i];\n\t}\n"

        #Sometimes add in some offset
        addOffset = random.randint(0,1)
        if (addOffset == 1):
            code += "\tsig" + str(componentNo) + " = sig" + str(componentNo) + " + sig" + str(componentNo-1) + " + " + randomHexValue(4) + ";\n"

        return code

    def inverter():
        # Reset code snippet
        code = "\t//NOTGATE\n\tint sig" + str(componentNo) + ";\n"
        #(Randomly) Extract a bit from the circuit
        prevSig = random.randint(1, max((componentNo - 1), 1))
        if (componentNo == 1 and prevSig == 1):
            prevSig = 0
        insertBit = random.randint(1, 31)
        code += "\tchar tempBit" + str(2 * componentNo) + "=(sig" + str(prevSig) + ">>" + str(
            insertBit) + ")&0x01;\n"

        #Perform bitwise operation
        code += "\tchar tempRes" + str(componentNo) + "=!((tempBit" + str(2 * componentNo) + ")&0x01);\n"

        #Insert result into random bit of input signal and output

        code += "\tsig" + str(componentNo) + "=sig" + str(prevSig) + ";\n"
        code += "\tsig" + str(componentNo) + " &= ~(1<<" + str(insertBit) + ");\n"
        code += "\tsig" + str(componentNo) + " |= (tempRes" + str(componentNo) + "<<" + str(insertBit) + ");\n"
        return code

    def incdecrementer():
        #Choose whether to implement incrementer or decrementer
        choice = random.randint(0,1)
        if (choice == 1):
            #Reset code snippet
            code = "\t//INCREMENTER\n\tvolatile int sig" + str(componentNo) + ";\n"

            #Determine how many times to iterate
            iterations = randomHexValue(4)
            code += "\tsig" + str(componentNo) + "=sig" + str(componentNo - 1) + ";\n"
            code += "\tfor(i=0; i<" + iterations + "; i++){\n"
            #code += "\t\tsig" + str(componentNo) + "=sig" + str(componentNo) + "++;\n"
            code += "\t\tsig" + str(componentNo) + "++;\n"
            code += "\t}\n"
        else:
            # Reset code snippet
            code = "\t//DECREMENTER\n\tvolatile int sig" + str(componentNo) + ";\n"

            # Determine how many times to iterate
            iterations = randomHexValue(4)
            code += "\tsig" + str(componentNo) + "=sig" + str(componentNo - 1) + ";\n"
            code += "\tfor(i=0; i<" + iterations + "; i++){\n"
            # code += "\t\tsig" + str(componentNo) + "=sig" + str(componentNo) + "--;\n"
            code += "\t\tsig" + str(componentNo) + "--;\n"
            code += "\t}\n"

        return code

    def shellSort():
        #Reset code snippet
        code = "\t//SHELL SORT\n"
        usePrevArray = random.randint(0,1)
        if (prev1dArray[0] == 0 or (prev1dArray[0] != 0 and usePrevArray == 0)):
            code += "\tvolatile int DimArray" + str(3*componentNo) + "[] = {" + randomHexValue(4)
            arraySize = random.randint(5,10)
            prev1dArray[0] = 3*componentNo
            for element in range(arraySize):
                code += ","
                usePrevSig = random.randint(0,1)
                if (usePrevSig == 1):
                    code += "sig" + str(random.randint(0,componentNo-1))
                else:
                    code += randomHexValue(4)
            code += "};\n\t"
            code += "volatile int n" + str(componentNo) + "= sizeof(DimArray" + str(
                3*componentNo) + ")/sizeof(DimArray" + str(3*componentNo) + "[0]);\n\t"
            code += "bubbleSort(DimArray" + str(3*componentNo) + ", n" + str(componentNo) + ");\n"
            code += "\tvolatile int sig" + str(componentNo) + "=DimArray" + str(3*componentNo) + "[" + str(random.randint(1,arraySize)) + "];\n"
        else:
            code += "\tvolatile int n" + str(componentNo) + "= sizeof(DimArray" + str(
                prev1dArray[0]) + ")/sizeof(DimArray" + str(prev1dArray[0]) + "[0]);\n\t"
            code += "shellSort(DimArray" + str(prev1dArray[0]) + ", n" + str(componentNo) + ");\n"
            code += "\tint sig" + str(componentNo) + " = DimArray" + str(prev1dArray[0]) + "[1];\n"
        return code

    def multiplexer():
        #Reset code snippet
        code = "\t//MULTIPLEXER\n\tint sig" + str(componentNo) + ";\n\t"

        #Determine size of multiplexer
        multiplexSize = random.randint(1,3)

        #Declare select bits
        for selectBit in range(multiplexSize):
            code += "char select" + str(5*componentNo + selectBit) + "=" + str(random.randint(0,1)) + "; "
        code += "\n\t"

        #Declare multiplexer inputs
        for muInput in range(pow(2,multiplexSize)):
            usePrevSig = random.randint(0,1)
            if (usePrevSig == 1):
                code += "volatile int mu" + str(32*componentNo + muInput) + "=sig" + str(random.randint(1,max(componentNo-1,1))) + "; "
            else:
                code += "volatile int mu" + str(32*componentNo + muInput) + "=" + randomHexValue(4) + "; "
        code += "\n"

        #Branching if statements
        def printMultiplexerOutputs(multiplexOutput):
            code =""
            for tabs in range(depth[0]+1):
                code += "\t"
            code += "if(select" + str(5*componentNo+depth[0]) + "){\n"
            for tabs in range(depth[0]+1):
                code += "\t"
            code += "\tsig" + str(componentNo) + "=mu" + str(32*componentNo+multiplexOutput) +";}\n"

            for tabs in range(depth[0]+1):
                code += "\t"
            code += "else if(select" + str(5*componentNo+depth[0]) + "){\n"
            for tabs in range(depth[0]+1):
                code += "\t"
            code += "\tsig" + str(componentNo) + "=mu" + str(32*componentNo+multiplexOutput+1) +";\n"

            return code
        multiplexOutput = [0]
        multiplexOutput[0] = 0
        depth = [0]
        depth[0] = 0
        tempCode = [0]
        tempCode[0] = ""
        #for depth in range(multiplexSize):
        def printMultiplex(multiplexSize):
            if(depth[0] < multiplexSize-1):
                #Print tab spaces
                for tabs in range(depth[0]+1):
                    tempCode[0] += "\t"
                #Print if conditionals
                tempCode[0] +="if(select" + str(5*componentNo + depth[0]) + "){\n"
                depth[0] +=1
                printMultiplex(multiplexSize)
                depth[0] -=1
                for tabs in range(depth[0] + 1):
                    tempCode[0] += "\t"
                tempCode[0] += "}\n"
            else:
                tempCode[0] += printMultiplexerOutputs(multiplexOutput[0])
                multiplexOutput[0] +=2

                for tabs in range(depth[0] + 1):
                    tempCode[0] += "\t"
                tempCode[0] += "}\n"



            if (depth[0] < multiplexSize - 1):
                # Print tab spaces
                for tabs in range(depth[0] + 1):
                    tempCode[0] += "\t"
                # Print if conditionals
                tempCode[0] += "if(!select" + str(5 * componentNo + depth[0]) + "){\n"
                depth[0] += 1
                printMultiplex(multiplexSize)
                depth[0] -=1
                for tabs in range(depth[0] + 1):
                    tempCode[0] += "\t"
                tempCode[0] += "}\n"


        printMultiplex(multiplexSize)
        code += tempCode[0]
        return code

    def multiplier():
        #Reset code snippet
        code = "\t//MULTIPLIER\n\tint sig" + str(componentNo) + ";\n"
        factor = random.randint(1,32)
        code += "\tsig" + str(componentNo) + "=sig" + str(componentNo-1) + "*" + str(factor) + ";\n"
        return code

    def divider():
        #Reset code snippet
        code = "\t//DIVIDER\n\tint sig" + str(componentNo) + ";\n"
        code += "\tfloat inter" + str(componentNo) + ";\n"
        usePrevSig = random.randint(0,1)
        if (usePrevSig==1):
            prevSig = random.randint(1,max(componentNo-1,1))
            code += "\tinter" + str(componentNo) + "=sig" + str(componentNo-1) +" / sig" + str(prevSig) +";\n"
        else:
            factor = random.randint(1,32)
            code += "\tinter" + str(componentNo) + "=sig" + str(componentNo - 1) + "/" + str(factor) + ";\n"
        code += "\tsig" + str(componentNo) + " = (int)inter" + str(componentNo) + ";\n"
        return code

    def bubbleSort():
        #Reset code snippet
        code = "\t//BUBBLE SORT\n"
        usePrevArray = random.randint(0,1)
        if(prev1dArray[0] == 0 or (prev1dArray[0] != 0 and usePrevArray == 0)):
            code += "\tvolatile int DimArray" + str(3*componentNo) + "[] = {" + randomHexValue(4)
            arraySize = random.randint(10,25)
            prev1dArray[0] = 3*componentNo
            for element in range(arraySize):
                code += ","
                usePrevSig = random.randint(0,1)
                if (usePrevSig == 1):
                    code += "sig" + str(random.randint(0,componentNo-1))
                else:
                    code += randomHexValue(4)
            code += "};\n\t"
            code += "volatile int n" + str(componentNo) + "= sizeof(DimArray" + str(
                3*componentNo) + ")/sizeof(DimArray" + str(3*componentNo) + "[0]);\n\t"
            code += "bubbleSort(DimArray" + str(3*componentNo) + ", n" + str(componentNo) + ");\n"
            code += "\tvolatile int sig" + str(componentNo) + "=DimArray" + str(3*componentNo) + "[" + str(random.randint(1,arraySize)) + "];\n"
        else:
            code += "\tvolatile int n" + str(componentNo) + "= sizeof(DimArray" + str(
                prev1dArray[0]) + ")/sizeof(DimArray" + str(prev1dArray[0]) + "[0]);\n\t"
            code += "bubbleSort(DimArray" + str(prev1dArray[0]) + ", n" + str(componentNo) + ");\n"
            code += "\tvolatile int sig" + str(componentNo) + "=DimArray" + str(prev1dArray[0]) + "[" + str(random.randint(1,5)) + "];\n"

        return code

    def matrixMul():
        code = "\t//2D MATRIX MULTIPLICATION\n\tvolatile int sig" + str(componentNo) + ";\n"
        arraySize = random.randint(3,5)
        prev2dArray[0] = 2*componentNo
        code += "\t#define N" + str(componentNo) + " " + str(arraySize) + "\n"
        code += "\tvolatile int n" + str(componentNo) + "=N" + str(componentNo) + ";\n"

        #Declare & initialise 2x2D matrices
        code += "\tvolatile int mulMatrix" + str(2*componentNo) + "[N" + str(componentNo) + "][N" + str(componentNo) + "]={"
        for row in range(arraySize):
            code += "{" + randomHexValue(4)
            for element in range(arraySize-1):
                code += "," + randomHexValue(4)
            if (row == arraySize-1):
                code += "}};\n"
            else:
                code += "},\n\t\t\t\t\t"
        #----------------
        code += "\tvolatile int mulMatrix" + str(2 * componentNo+1) + "[N" + str(componentNo) + "][N" + str(
            componentNo) + "]={"
        for row in range(arraySize):
            code += "{" + randomHexValue(4)
            for element in range(arraySize - 1):
                code += "," + randomHexValue(4)
            if (row == arraySize-1):
                code += "}};\n"
            else:
                code += "},\n\t\t\t\t\t"

        code += "\tvolatile int res" + str(componentNo) + "[N" + str(componentNo) + "][" + str(componentNo) + "];\n"
        code += "\tsig" + str(componentNo) + "=matrixmul2d(n" + str(componentNo) + ",mulMatrix" + str(2*componentNo) + ",mulMatrix" + str(2*componentNo+1) + ",res" + str(componentNo) + ");\n"
        return code

    def kthlargestelement():
        code = "\t//Kth LARGEST ELEMENT\n"
        code += "\tvolatile int sig" + str(componentNo) + "=sig" + str(componentNo-1) + ";\n"
        #Use previously declared array if available
        if (prev1dArray[0] != 0):
            code += "\tvolatile char sizeOfArray" + str(componentNo) + "="
            code += "sizeof(DimArray" + str(prev1dArray[0]) + ")/sizeof(DimArray" + str(prev1dArray[0]) + "[0]);\n"
            code += "\tvolatile char k" + str(componentNo) + "=" +str(random.randint(1,10)) + ";\n"
            code += "\tsig" + str(componentNo) + "=quickselect(DimArray" + str(prev1dArray[0]) + ",0, (sizeOfArray" + str(componentNo) + "-1),k" + str(componentNo) + ");\n"
        else:
            code += "\tvolatile int DimArray" + str(3*componentNo) + "[] = {" + randomHexValue(4)
            arraySize = random.randint(10, 25)
            prev1dArray[0] = 3*componentNo
            for element in range(arraySize):
                code += ","
                usePrevSig = random.randint(0, 1)
                if (usePrevSig == 1):
                    code += "sig" + str(random.randint(0, componentNo - 1))
                else:
                    code += randomHexValue(4)
            code += "};\n\t"
            code += "volatile int sizeOfArray" + str(componentNo) + "= sizeof(DimArray" + str(
                3*componentNo) + ")/sizeof(DimArray" + str(3*componentNo) + "[0]);\n"
            code += "\tvolatile char k" + str(componentNo) + "=" + str(random.randint(1, 10)) + ";\n"
            code += "\tsig" + str(componentNo) + "=quickselect(DimArray" + str(
                prev1dArray[0]) + ",0, (sizeOfArray" + str(componentNo) + "-1),k" + str(componentNo) + ");\n"
        return code

    def matrixInverse():
        code = "\t//INVERSE MATRIX\n"
        arraySize = random.randint(3,5)
        code += "\tvolatile int sig" + str(componentNo) + ";\n"
        code += "\tchar k" + str(componentNo) + ", d" + str(componentNo) + ";\n"
        if (prev2dArray[0] != 0):
            code += "\tvolatile int invMatrix" + str(componentNo) + "[" + str(arraySize) + "][" + str(arraySize) + "];\n"
            code += "\tfor(i=0; i<" + str(arraySize-1) + "; i++){\n"
            code += "\t\tfor(j=0; j<" + str(arraySize - 1) + "; j++){\n"
            code += "\t\t\tinvMatrix" + str(componentNo) + "[i][j] = (char)mulMatrix" + str(prev2dArray[0]) + "[i][j];\n"
            code += "\t\t}\n\t}\n"
        else:
            # Declare & initialise 2x2D matrices
            code += "\tvolatile int invMatrix" + str(componentNo) + "[" + str(arraySize) + "][" + str(
                arraySize) + "]={"
            for row in range(arraySize):
                code += "{" + randomHexValue(4)
                for element in range(arraySize - 1):
                    code += "," + randomHexValue(4)
                if (row == arraySize - 1):
                    code += "}};\n"
                else:
                    code += "},\n\t\t\t\t\t"

        code += "\td" + str(componentNo) + "=determinant(" + str(arraySize) + ",invMatrix" + str(componentNo) + ", k" + str(componentNo) + ");\n"
        code += "\tif(d" + str(componentNo) + "!=0){\n\t\tcofactor(" + str(arraySize) + ", invMatrix" + str(componentNo) + ", k" + str(componentNo) + ");\n\t}\n"
        code += "\tsig" + str(componentNo) + "=d" + str(componentNo) + ";\n"
        return code

    components = { 1: logicGate,
                   2: bubbleSort,
                   3: matrixMul,
                   4: incdecrementer,
                   5: shellSort,
                   6: multiplexer,
                   7: multiplier,
                   8: adder,
                   9: kthlargestelement,
                   10: inverter,
                   11: matrixInverse}

    returnedCode = components[componentChoice]()
    with open(savePathTxt, "a") as myFile:
        myFile.write(str(returnedCode) + "\n")
    # APPEND RETURNED TEXT FROM CASE STAT. TO TXT FILE

def randomHexValue(length):
    return "0x" + str(binascii.b2a_hex(os.urandom(length)).decode("utf-8"))