import fetchImageFromQwant as getImg
import processImage as procImg
import createGcode as crtGc
import convertImage as cvtImg
import sys
import selenium
import traceback
import subprocess

from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, Close


def deleteFile(fileCreated):
    for file in fileCreated:
        subprocess.run(["rm", '.'.join(file)])


if __name__ == '__main__':
    fileCreated = []
    try :
        fileCreated.extend(getImg.getImage(fileCreated, sys.argv[1]))

        if(fileCreated[-1][1] != 'jpg'):
            fileCreated.append(cvtImg.convertImageToJpg(fileCreated))

        fileCreated.append(procImg.detectEdge(fileCreated))

        fileCreated.extend(cvtImg.convertImageToSvg(fileCreated))

        crtGc.writeGcode(fileCreated, ["output", "gcode"])


    except selenium.common.exceptions.TimeoutException as err:
        traceback.print_exc()
        print("Most of the time, due to no result")
    except Exception as err:
        traceback.print_exc()
    finally:
        print("Those file will be delete {0}".format(fileCreated))
        # deleteFile(fileCreated)
