import subprocess

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
