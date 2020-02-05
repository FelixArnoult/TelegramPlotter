from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage import util as skUtil
import numpy as np
from PIL import Image

def load_image(infilename):
    img = Image.open( infilename )
    img.load()
    data = np.asarray( img)
    return data

def save_image(npdata, outfilename):
    Image.fromarray((npdata * 255).astype('uint8'), mode='L').save('.'.join(outfilename))

def detectEdge(fileCreated):
    img = load_image('.'.join(fileCreated[-1]))
    imgGrey = rgb2gray(img)
    edgeimage = skUtil.invert(sobel(imgGrey))
    edgedFileName = [fileCreated[-1][0] + '_edged', fileCreated[-1][1]]
    save_image(edgeimage, edgedFileName)
    return edgedFileName
