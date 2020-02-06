import fetchImageFromQwant as getImg
import processImage as procImg
import createGcode as crtGc
import subprocess
import sys
import selenium
import traceback

from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, Close

def convertImageToJpg(fileCreated):
    convertedFile = [fileCreated[-1][0], 'jpg']
    subprocess.run(["convert", '.'.join(fileCreated[-1]), '-background', 'white', '-flatten', '-alpha', 'off', '.'.join(convertedFile)])
    return convertedFile

def convertImageToSvg(fileCreated):
    convertedFiles = []
    tempFile = [fileCreated[-1][0], 'pnm']
    subprocess.run(["convert", '.'.join(fileCreated[-1]), '-resize', '3700x2000', '.'.join(tempFile)])
    convertedFiles.append(tempFile)
    outputFile = [fileCreated[-1][0], 'svg']
    subprocess.run(["potrace", '.'.join(convertedFiles[-1]), '-s', '-o', '.'.join(outputFile)])
    convertedFiles.append(outputFile)
    return convertedFiles

def deleteFile(fileCreated):
    for file in fileCreated:
        subprocess.run(["rm", '.'.join(file)])


if __name__ == '__main__':
    fileCreated = []
    try :
        fileCreated.extend(getImg.getImage(fileCreated, sys.argv[1]))

        if(fileCreated[-1][1] != 'jpg'):
            fileCreated.append(convertImageToJpg(fileCreated))

        fileCreated.append(procImg.detectEdge(fileCreated))

        fileCreated.extend(convertImageToSvg(fileCreated))

        crtGc.writeGcode(fileCreated, ["output", "gcode"])


    except selenium.common.exceptions.TimeoutException as err:
        traceback.print_exc()
        print("Most of the time, due to no result")
    except Exception as err:
        traceback.print_exc()
    finally:
        print("Those file will be delete {0}".format(fileCreated))
        # deleteFile(fileCreated)
