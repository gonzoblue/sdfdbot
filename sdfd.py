#!/usr/bin/env python
#https://github.com/gonzoblue/sdfdbot
#Automated SDFD incident page scraping and alerting
#Not official or affiliated with SDFD in any way
#all imports go at the top
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
from twitter.api import Twitter
from requests import Session

#Set up the database
callsdb_file = '/home/pi/sdfdbot/callsdb.sqlite'
db = sqlite3.connect(callsdb_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS calls (dbid INTEGER PRIMARY KEY, dbcalldate TEXT, dbcalltype TEXT, dbstreet TEXT, dbcross TEXT, dbunitids TEXT, dbnumunits INTEGER, dbupdatetime timestamp, dbalertsent INTEGER DEFAULT 0)')
db.commit()

#Save a fully built call to the database
def storeCall(fullCall):
  fullCall = fullCall + " (" + str(numUnits) + ") @ " + savedCallDate
  c.execute('SELECT dbid FROM calls WHERE dbcalldate=?', (savedCallDate,))
  callid = c.fetchone()
  if callid > 0:
     c.execute('SELECT * FROM calls WHERE dbid=?', (callid))
     print "=" + str(c.fetchone())
  else:
    now = datetime.now()
#    print "Saving" + savedCallType + " " + savedCallStreet + " as " + savedCallDate + " with timestamp " + now.strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO calls(dbcalldate, dbcalltype, dbstreet, dbcross, dbunitids, dbnumunits, dbupdatetime) VALUES(?,?,?,?,?,?,?)', (savedCallDate, savedCallType, savedCallStreet, savedCallCross, units, numUnits, now))
    db.commit()
    c.execute('SELECT * FROM calls WHERE dbcalldate=?', (savedCallDate,))
    print "+" + str(c.fetchone())
    sendAlert(fullCall)

#Send an alert if the call is the right type
def sendAlert(fullCall):
  print "Alerting: " + fullCall
  return

# Dump the HTML, turn in to BeautifulSoup object, find and save the table
print "Starting...\n"
with Session() as session:
    r = session.get('http://apps.sandiego.gov/sdfiredispatch/') #context manager closes things neatly
#r = requests.get('http://localhost/sdfd.html')
soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr("id") and tag['id']=="gv1")

# Variables
savedCallDate = "none"
callDesc = []

# Run through each row and pick apart the call details
for row in table.findAll("tr"):
  call = row.findAll("td")
  if len(call) == 5: 
    date = str(call[0].get_text().strip())
    calltype = str(call[1].get_text().strip())
    street = str(call[2].get_text().strip())
    cross = str(call[3].get_text().strip())
    unitid = str(call[4].get_text().strip())
# Build the incident string, adding units each time. If a new incident is found, save the call.
    if savedCallDate != date:
      if savedCallDate != "none":
        storeCall(callDesc)
      callDesc = "[" + calltype + "] " + street + " - " + unitid
      units = unitid
      numUnits = 1
    else:
      callDesc = callDesc + ", " + unitid
      units = units + ", " + unitid
      numUnits = numUnits + 1
    savedCallDate = date
    savedCallType = calltype
    savedCallStreet = street
    savedCallCross = cross
# Save the last call built
storeCall(callDesc)

db.close()
print "\nFinished."
exit()
