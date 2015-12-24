import os
import sys
import fnmatch
import pygame
from pygame.locals import *
import datetime
import random
import string
import urllib
from itertools import cycle
import configparser

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

    return str(shouldBeOn)+" "+str(istime)+" "+str(offtime)

def albumName(name):
    newname = name.replace('_', ' ')
    newname = newname.capitalize()
    return newname

def getImages(folder):
    global xcycle
    global picLen
    xfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    #for f in xfiles:
    #    os.rename(f, f.replace(' ', '_'))
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
    return 'static/images/'+currentfolder+'/'+bg, albumName(currentfolder), date, jfolder+'/'+bg

## Get date and check for special dates (christmas etc)
now = datetime.datetime.now()
timeString = now.strftime("%d %m %Y")
timeMonth = now.strftime("%m")
timeDay = now.day

#if timeMonth == "12":
#    xmas = True
    
def calculate_image_size(image):
    """Calculates width and height of image in pixels.
    Args:
        image as string (path to image).
    Returns:
        tuple (int image width in pixels, int image height in pixels).
    """
    img = Image.open(image)  # Pillow Image Class Method (open).
    image_width, image_height = img.size
    if image_width > 1280 and image_height > 800:
        system("mogrify -resize 1280x800^ "+image)
        img = Image.open(image)
    return img.size  # Pillow Image Class Attribute (size).
# end calculate_image_size()


def calculate_screen_size():
    """Calculates width and height of screen in pixels.
    Returns:
        tuple (int screen width in pixels, int screen height in pixels).
    """
    return pygame.display.Info().current_w, pygame.display.Info().current_h
# end calculate_screen_size()


def calculate_xy_coords(image_size, screen_size):
    """Calculates x and y coordinates used to display image centered on screen.
    Args:
        image_size as tuple (int width in pixels, int height in pixels).
        screen_size as tuple (int width in pixels, int height in pixels).
    Returns:
        tuple (int x coordinate, int y coordinate).
    """
    image_width, image_height = image_size
    screen_width, screen_height = screen_size
    x = (screen_width - image_width) / 2
    y = (screen_height - image_height) / 2
    return (x, y)
# end calculate_xy_coords()


def check_for_quit():
    """Quits the program if the user presses either the [ESC] key
    or the [q] key.
    Returns:
        None.
    """
    for event in pygame.event.get():
        if event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
            pygame.display.quit()
            pygame.quit()
            sys.exit(0)
# end check_for_quit()


def clear_screen(screen):
    """Clears the screen by filling it with black.
    Args:
        screen as object.
    Returns:
        None.
    """
    screen.fill([0, 0, 0])
# end clear_screen()
    
def display_image(image, screen, xy_coords):
    """Bit Block Transfers (displays) the image to screen.
    Args:
        image as string (path to image).
        screen as object.
        xy_coords as tuple (int x coordinate, int y coordinate). Specifies where to draw the image on screen.
    Returns:
        None.
    """
    img = pygame.image.load(image)  # Load the image file from disk.
    screen.blit(img, xy_coords)  # BLIT image to screen
    
# end display_image()

def display_date(date, screen, myfont):
    datetaken = myfont[0].render(date, 1, (250,250,250))
    screen.blit(datetaken, (5, 770))
    
    
    date = myfont[1].render(, 1, (250,250,250))
    screen.blit(date, (10,760))

def play_slide_show(screen, screen_size, myfont):
    global jfolder
    global picLen, picNum, REFRESH_TIME
    
    display = checkDisplayTimetable()
    
    #if timeMonth == "12" and timeDay > 23 and timeDay < 27:
    #    bg, album, date = christmas()
    #else:
    bg, album, date, path = normal()
        
    #imagesshown.append(bg)
    #bg = bg.replace(' ','%20')
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
    
    check_for_quit()

    #image = slide_show_path + image_list[image_list_index]  # Create the path to the image.

    image_size = calculate_image_size(path)

    # Calculate xy coordinates used to display image centered on screen.
    xy_coords = calculate_xy_coords(image_size, screen_size)

    display_image(path, screen, xy_coords)
    display_date(date, screen, myfont)
    pygame.display.flip()  # Update the screen.
    sleep(30) 
    # Wait for number of seconds.
    clear_screen(screen)

def main():

    pygame.init()
    screen_size = calculate_screen_size()

    myfont = (pygame.font.SysFont("Helvetica", 15), pygame.font.SysFont("Helvetica", 30), pygame.font.SysFont("Helvetica",25))
    # Create the pygame screen used to display images.
    # Displays slide show full screen.
    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

    # Create the pygame screen used to display images.
    # Displays slide show in screen_size window instead of full screen.
    #    screen = pygame.display.set_mode(screen_size)

    pygame.mouse.set_visible(0)  # Hide the mouse cursor.

    while True:

        play_slide_show(screen, screen_size, myfont)

# end main()

if __name__ == '__main__':
    main()
