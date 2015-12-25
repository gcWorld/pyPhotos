from flask import Flask, render_template, request
import datetime
import random
import string
import urllib
from itertools import cycle
import configparser
app = Flask(__name__)

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
    

@app.route("/", methods=['GET', 'POST'])
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
    app.run(host='0.0.0.0', port=80, debug=False)
