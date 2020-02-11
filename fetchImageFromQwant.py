import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import urllib.request
import random

numberOfImage = 5



def getBrowser():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    return webdriver.Chrome(chrome_options=options)

def selectRandomImage(images):
    selected = random.randint(0, len(images)-1)
    images[selected], images[-1] = images[-1], images[selected]
    return images

def getImage(fileCreated, keyword):
    images = fetchImages(fileCreated, keyword)
    selectRandomImage(images)
    # print(images)
    return images

def fetchImages(fileCreated, keyword):
    fetchedImages = []
    url = "https://www.qwant.com/?q=coloriage%20"+keyword+"&t=images"#&color=monochrome&imagetype=transparent"
    print(url)
    browser = getBrowser()
    browser.get(url)
    counter = 0
    succounter = 0
    timeout = 10
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'result--images'))
        WebDriverWait(browser, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        raise

    for x in browser.find_elements_by_xpath("//div[contains(@class, 'result--images')]"):
        name = './image/' + str(keyword) + str(counter)
        counter = counter + 1
        url = x.find_element_by_tag_name('a').get_attribute('href')
        imgtype = url.split(".").pop()
        try :
            fetchedImages.append(saveImage(url, [name, imgtype]))
            if counter >= numberOfImage :
                break
        except Exception as e:
            print(e)
            print( "can't get img")
    browser.close()
    return fetchedImages


def saveImage(url, outfile):
    print(url)
    response = urllib.request.urlopen(url)
    image = response.read()
    with open('.'.join(outfile), 'wb') as f:
        f.write(image)
    return outfile


# if __name__ == '__main__':
#     fetchImages(sys.argv[1])
