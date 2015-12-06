from flask import Flask, render_template
import datetime
import random
import string
import urllib
from itertools import cycle
app = Flask(__name__)

## Variable definition
REFRESH_TIME='30' #in seconds

currentfolder = ""
bg = ""
jfolder = ""
picLen = 0
picNum = 0
imagesshown = []
mypath = '/home/pi/pyphotos/static/images'
    

from PIL import Image

def get_date_taken(path):
    try:     
        datetaken = str(Image.open(path)._getexif()[36868])
    except:
        return ""
    datetaken = datetaken[:-9]
    year = datetaken[:4]
    month = datetaken[5:7]
    day = datetaken[8:10]
    #return datetaken
    return day+'.'+month+'.'+year 

from os import listdir, system
from os.path import isfile, isdir, join

folder = [x for x in listdir(mypath) if isdir(join(mypath,x))]
#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def albumName(name):
    newname = name.replace('_', ' ')
    newname = newname.capitalize()
    return newname

def getImages(folder):
    global xcycle
    global picLen
    xfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    xfiles.sort()
    picLen = len(xfiles)
    xcycle = cycle(xfiles)
    #bg = random.choice(xfiles)
    #shown = [i for i in imagesshown if bg in i]
    return xfiles, xcycle

def getFolder():
    global jfolder
    global currentfolder
    fold = [s for s in folder]
    try:
        currentfolder = random.choice(fold)
    except:
        return "error", "error"
    jfolder = mypath + '/' +currentfolder
    return jfolder, currentfolder

def christmas():
    sub = "weihnachten"
    xmas = [s for s in folder if sub in s]
    currentfolder = random.choice(xmas)
    jfolder = mypath + '/' +currentfolder
    xfiles = [f for f in listdir(jfolder) if isfile(join(jfolder, f))]
    bg = random.choice(xfiles)
    date = get_date_taken(jfolder+'/'+bg)
    return 'static/images/'+currentfolder+'/'+bg, albumName(currentfolder), date

def normal():
    global xcycle
    global jfolder
    global currentfolder, picNum
    if not jfolder or picNum+1 > picLen:
        jfolder, currentfolder = getFolder()
        if jfolder == "error":
            return "", "Keine Bilder", ""
        xfiles, xcycle= getImages(jfolder)
        picNum = 0
    bg = next(xcycle)
    picNum += 1
    #i=0
    #while shown:
    #    bg, shown = getImages(jfolder)
    #    i = i + 1
    #    if i > 50:
    #        break
    
    date = get_date_taken(jfolder+'/'+bg)
    return 'static/images/'+currentfolder+'/'+bg, albumName(currentfolder), date

## Get date and check for special dates (christmas etc)
now = datetime.datetime.now()
timeString = now.strftime("%d %m %Y")
timeMonth = now.strftime("%m")
timeDay = now.day

if timeMonth == "12":
    xmas = True

@app.route("/")
def hello():
    global jfolder
    global picLen, picNum, REFRESH_TIME
    if timeMonth == "12" and timeDay > 23 and timeDay < 27:
        bg, album, date = christmas()
    else:
        bg, album, date = normal()
        
    imagesshown.append(bg)
    bg = bg.replace(' ','%20')
    templateData = {
        'title' : 'HELLO!',
        'date' : date,
        'bg' : urllib.parse.urlparse(bg).geturl(),
        #'bg' : 'static/images/weihnachten/DSC_0338.JPG',
        'images' : str(picNum)+'/'+str(picLen)+' '+bg,
        'refreshtime' : REFRESH_TIME,
        'album' : album
    }
    return render_template('index.html', **templateData)
    
@app.route("/settings")
def settings():
    templateData = {
        'title' : "Einstellungen"
    }
    return render_template('settings.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
