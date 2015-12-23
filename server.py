from flask import Flask, render_template, request
import datetime
import random
import string
import urllib
from itertools import cycle
import configparser
app = Flask(__name__)

import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)

config = configparser.ConfigParser()
config.read('/home/pi/pyphotos/settings.cfg')

## Variable definition
REFRESH_TIME=config['General']['refreshtime'] #in seconds

currentfolder = ""
bg = ""
jfolder = ""
picLen = 0
picNum = 0
displayon = True
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

def toggleDisplay():
    GPIO.setup(16, GPIO.OUT, initial=1)
    GPIO.output(16, 0)         # this is our simulated button press
    sleep(0.2)                 # hold button for 0.2 seconds
    GPIO.output(16, 1)         # release button
    GPIO.setup(16, GPIO.IN)    # set port back to input (re-enables buttons)

def checkDisplayTimetable():
    global displayon
    now = datetime.datetime.now()
    timeWeekDay = now.strftime("%a")
    timeHour = now.strftime("%H")
    timeMinute = now.strftime("%M")
    
    if timeWeekDay == "Mon":
        ontime = config['Timetable']['mon-on-1']
        offtime = config['Timetable']['mon-off-1']
    elif timeWeekDay == "Tue":
        ontime = config['Timetable']['tue-on-1']
        offtime = config['Timetable']['tue-off-1']
    elif timeWeekDay == "Wed":
        ontime = config['Timetable']['wed-on-1']
        offtime = config['Timetable']['wed-off-1']
    elif timeWeekDay == "Thu":
        ontime = config['Timetable']['thu-on-1']
        offtime = config['Timetable']['thu-off-1']
    elif timeWeekDay == "Fri":
        ontime = config['Timetable']['fri-on-1']
        offtime = config['Timetable']['fri-off-1']
    elif timeWeekDay == "Sat":
        ontime = config['Timetable']['sat-on-1']
        offtime = config['Timetable']['sat-off-1']
    elif timeWeekDay == "Sun":
        ontime = config['Timetable']['sun-on-1']
        offtime = config['Timetable']['sun-off-1']
    
    ontime = ontime.split(':')
    ontime = int(ontime[0])*60 + int(ontime[1])
    
    offtime = offtime.split(':')
    offtime = int(offtime[0])*60 + int(offtime[1])
    
    istime = int(timeHour)*60 + int(timeMinute)
    
    if istime > ontime and istime < offtime:
        shouldBeOn = True
    else:
        shouldBeOn = False
        
    if shouldBeOn and not displayon:
        toggleDisplay()
        displayon = True
    elif not shouldBeOn and displayon:
        toggleDisplay()
        displayon = False

    return shouldBeOn

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
    
    display = checkDisplayTimetable()
    
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
        #'images' : str(picNum)+'/'+str(picLen)+' '+bg,
        'images' : display,
        'refreshtime' : REFRESH_TIME,
        'album' : album
    }
    return render_template('index.html', **templateData)
    
@app.route("/settings", methods=['GET', 'POST'])
def settings():
    global config
    config.read('/home/pi/pyphotos/settings.cfg')
    if request.method == 'POST':
        refreshtime = request.form['refreshtime']
        config.set('General', 'refreshtime', refreshtime)
        config.set('Timetable', 'mon-on-1', request.form['mon-on-1'])
        config.set('Timetable', 'mon-off-1', request.form['mon-off-1'])
        config.set('Timetable', 'tue-on-1', request.form['tue-on-1'])
        config.set('Timetable', 'tue-off-1', request.form['tue-off-1'])
        config.set('Timetable', 'wed-on-1', request.form['wed-on-1'])
        config.set('Timetable', 'wed-off-1', request.form['wed-off-1'])
        config.set('Timetable', 'thu-on-1', request.form['thu-on-1'])
        config.set('Timetable', 'thu-off-1', request.form['thu-off-1'])
        config.set('Timetable', 'fri-on-1', request.form['fri-on-1'])
        config.set('Timetable', 'fri-off-1', request.form['fri-off-1'])
        config.set('Timetable', 'sat-on-1', request.form['sat-on-1'])
        config.set('Timetable', 'sat-off-1', request.form['sat-off-1'])
        config.set('Timetable', 'sun-on-1', request.form['sun-on-1'])
        config.set('Timetable', 'sun-off-1', request.form['sun-off-1'])
        with open('/home/pi/pyphotos/settings.cfg', 'w') as configfile:
            config.write(configfile)
        templateData = {}
        return render_template('settings-post.html', **templateData)
    else:
        #config.add_section('General')
        #config.set('General', 'refreshtime', '30')
        # Writing our configuration file to 'example.cfg'
        #with open('settings.cfg', 'w') as configfile:
        #    config.write(configfile)
        specialdates_checked = ""
        if config['General']['specialdates']:
            specialdates_checked = "checked='checked'"
        
        templateData = {
            'title' : "Einstellungen",
            'refreshtime' : config['General']['refreshtime'],
            'specialdates' : config['General']['specialdates'],
            'specialdates_checked' : specialdates_checked,
            'monon1' : config['Timetable']['mon-on-1'],
            'monoff1' : config['Timetable']['mon-off-1'],
            'tueon1' : config['Timetable']['tue-on-1'],
            'tueoff1' : config['Timetable']['tue-off-1'],
            'wedon1' : config['Timetable']['wed-on-1'],
            'wedoff1' : config['Timetable']['wed-off-1'],
            'thuon1' : config['Timetable']['thu-on-1'],
            'thuoff1' : config['Timetable']['thu-off-1'],
            'frion1' : config['Timetable']['fri-on-1'],
            'frioff1' : config['Timetable']['fri-off-1'],
            'saton1' : config['Timetable']['sat-on-1'],
            'satoff1' : config['Timetable']['sat-off-1'],
            'sunon1' : config['Timetable']['sun-on-1'],
            'sunoff1' : config['Timetable']['sun-off-1'],
        }
        return render_template('settings.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
