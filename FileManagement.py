import os, shutil, time

def cleanFolder(directory,extension):
    dirName = directory
    folderToClear = os.listdir(dirName)
    for item in folderToClear:
        if item.endswith(extension):
            os.remove(os.path.join(dirName, item))

def fetchAST(timestamp, mainLegUpFolder, scriptFolder):
    os.chdir(mainLegUpFolder)
    os.popen('clang -S -emit-ast -g test.c')
    while not os.path.exists(mainLegUpFolder + '/test.ast'):
        time.sleep(1)
    os.rename('test.ast', 'test' + timestamp + '.ast')
    astfile = mainLegUpFolder + '/test' + timestamp + '.ast'
    shutil.copy(astfile, scriptFolder)
    while not os.path.exists(scriptFolder + '/test' + timestamp + '.ast'):
        time.sleep(1)

def cleanAllFolders(mainLegUpFolder, bmpFolder):
    cleanFolder(bmpFolder, '.c')  # Clear C files
    #cleanFolder(bmpFolder + '/TXT', '.txt')  # Clear c file folder
    cleanFolder(mainLegUpFolder, '.ast')
    cleanFolder(mainLegUpFolder, '.c')
    cleanFolder((mainLegUpFolder + "/Hardware"), '.c')
