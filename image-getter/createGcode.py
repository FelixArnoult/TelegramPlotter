from svgpathtools import *
from pygcode import *
import numpy as np

diviseur = 100 #svg file is at scale 100
resolution = 0.5 #Length of each drawn segment

fastMove = 5000 #mm/min
slowMove = 3000 #mm/min

def writeGcode(inputfile, outputfile):
    # outputfile = ["output", "gcode"]
    gcodeFile = open('.'.join(outputfile),"w")
    init(gcodeFile)
    draw(gcodeFile, inputfile)
    end(gcodeFile)
    gcodeFile.close()
    return outputfile


def draw(outputfile, drawSvg):
    paths, attributes, svg_attributes = svg2paths2('.'.join(drawSvg[-1]))
    gcodes = []
    for path in paths:
        gcodeToAdd = []
        nbPoint = int(path.length()/diviseur/resolution)
        gcodeToAdd.append(GCodeFeedRate(fastMove))
        gcodeToAdd.append(GCodeStartSpindleCW(S=0)) #Raise pen up
        gcodeToAdd.append(GCodeLinearMove(X=np.real(path.point(0))/diviseur, Y=np.imag(path.point(0))/diviseur)) #Fast move to the first point of path
        gcodeToAdd.append(GCodeStartSpindleCW(S=1)) #Raise pen down

        gcodeToAdd.append(GCodeFeedRate(slowMove))

        for i in np.linspace(1/nbPoint, 1, nbPoint):
            imCoord = path.point(i)
            gcodeToAdd.append(GCodeLinearMove(X=np.real(imCoord)/diviseur, Y=np.imag(imCoord)/diviseur))
        gcodes.append(gcodeToAdd)
    file = ''
    for gcode in gcodes:
        writeOnFile(outputfile, gcode)

def init(outputfile):
    init = ["$H",   #Home
    "G90",          #Absolute mode
    "G92 X0 Y0",    #Set 0
    "M3 S0"]        #Raise pen up
    writeOnFile(outputfile, init)

def end(outputfile):
    end = ["M3 S0", #Raise pen up
    "$H"]           #Home
    writeOnFile(outputfile, end)

def writeOnFile(outputfile, content):
    for line in content :
        outputfile.write(str(line) + '\n')

# if __name__ == '__main__':
#     outputfile = open("output.gcode","w")
#     init(outputfile)
#     draw(outputfile, [["./image/smt", "svg"]])
#     end(outputfile)
#     outputfile.close()
