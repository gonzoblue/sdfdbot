#https://github.com/gonzoblue/sdfdbot
#Automated SDFD incident page scraping and alerting
#Not official or affiliated with SDFD in any way

#Set up the database
import sqlite3
callsdb_file = '/home/pi/sdfdbot/callsdb.sqlite'
db = sqlite3.connect(callsdb_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS calls (dbid INTEGER PRIMARY KEY, dbcalldate TEXT, dbcalltype TEXT, dbstreet TEXT, dbcross TEXT, dbunitids TEXT, dbnumunits INTEGER, dbupdatetime timestamp, dbalertsent INTEGER DEFAULT 0)')
db.commit()

#Function to alert on a fully built interesting call
def storeCall():
#  fullCall = fullCall + " (" + str(numUnits) + ") @ " + savedCallDate
#  coolCall = ['Fire', 'CPTR', 'Sdge']
#  if any(word in fullCall for word in coolCall):
#    print fullCall
#  elif numUnits > 9:
#    print fullCall
#  else:
#    print  "--" + fullCall
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

# Dump the HTML, turn in to BeautifulSoup object, find and save the table
print "Starting...\n"
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from twitter.api import twitter
r = requests.get('http://apps.sandiego.gov/sdfiredispatch/')
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
        storeCall()
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
storeCall()

db.close()
print "\nFinished."
exit()
