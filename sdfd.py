#https://github.com/gonzoblue/sdfdbot
#Automated SDFD incident page scraping and alerting
#Not official or affiliated with SDFD in any way

#Set up the database
import sqlite3
callsdb_file = '/home/pi/sdfdbot/stable/callsdb.sqlite'
db = sqlite3.connect(callsdb_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS calls (dbid INTEGER PRIMARY KEY, dbcalldate TEXT, dbcalltype TEXT, dbstreet TEXT, dbcross TEXT, dbunitids TEXT, dbnumunits INTEGER, dbupdatetime timestamp, dbalertsent INTEGER DEFAULT 0)')
db.commit()

#Function to alert on a fully built interesting call
def storeCall(fullCall):
#  coolCall = ['Fire', 'CPTR', 'Sdge']
#  if any(word in fullCall for word in coolCall):
#    print fullCall
#  elif numUnits > 9:
#    print fullCall
#  else:
#    print  "--" + fullCall
  fullCall = fullCall + " (" + str(numUnits) + ") @ " + savedCallDate
  c.execute('SELECT dbid FROM calls WHERE dbcalldate=?', (savedCallDate,))
  callid = c.fetchone()
  now = datetime.now()
  if callid > 0:
    callChanged = 0
    c.execute('SELECT * FROM calls WHERE dbid=?', (callid))
    oldEntry = c.fetchone()
    print "=" + str(oldEntry)
    oldCallType = str(oldEntry[2])
    oldStreet = str(oldEntry[3])
    oldCross = str(oldEntry[4])
    oldNumUnits = oldEntry[6]
# Check for updates to old calls
    if oldCallType != savedCallType:
      c.execute('UPDATE calls SET dbcalltype=? where dbid=?', (savedCallType, callid[0]))
      db.commit()
      callChanged=1
    elif oldStreet != savedCallStreet:
      c.execute('UPDATE calls SET dbstreet=? where dbid=?', (savedCallStreet, callid[0]))
      db.commit()
      callChanged=1
    elif oldCross != savedCallCross:
      c.execute('UPDATE calls SET dbcross=? where dbid=?', (savedCallCross, callid[0]))
      db.commit()
      callChanged=1
    elif oldNumUnits != numUnits:
      c.execute('UPDATE calls SET dbunitids=? where dbid=?', (units, callid[0]))
      c.execute('UPDATE calls SET dbnumunits=? where dbid=?', (numUnits, callid[0]))
      callChanged=1
    if callChanged==1:
      c.execute('UPDATE calls SET dbupdatetime=? where dbid=?', (now, callid[0]))
      db.commit()
      c.execute('SELECT * FROM calls WHERE dbcalldate=?', (savedCallDate,))
      print "$" + str(c.fetchone())
  else:
#    print "Saving" + savedCallType + " " + savedCallStreet + " as " + savedCallDate + " with timestamp " + now.strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO calls(dbcalldate, dbcalltype, dbstreet, dbcross, dbunitids, dbnumunits, dbupdatetime) VALUES(?,?,?,?,?,?,?)', (savedCallDate, savedCallType, savedCallStreet, savedCallCross, units, numUnits, now))
    db.commit()
    c.execute('SELECT * FROM calls WHERE dbcalldate=?', (savedCallDate,))
    print "+" + str(c.fetchone())
    sendAlert(fullCall)

def sendAlert(fullCall):
  tweet = twitter.Api(consumer_key='1',consumer_secret='2',access_token_key='3',access_token_secret='4')
  status = tweet.PostUpdate(fullCall)
  print "Tweet sent: " + status.text
  coolCall = ['CPTR', 'CRATER', 'Fire', 'Residential', 'Structure Fire', 'Sdge', 'PENTICTON', 'CAPRICORN']
  if any(word in fullCall for word in coolCall):
    sendEmail()
  elif numUnits > 10:
    sendEmail()
  return

def sendEmail():
  print "Emailing Call Type: [" + savedCallType + "]"
  fromaddr = "me@mail.com"
  toaddr = "you@mail.com"
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject']= savedCallType + " | " + savedCallStreet + " | " + str(numUnits)
  body = savedCallType + " | " + units
  msg.attach(MIMEText(body, 'plain'))
  email = smtplib.SMTP('mail.com', 587)
  email.ehlo()
  email.starttls()
  email.ehlo()
  email.login("me@mail.com","mypass")
  text = msg.as_string()
  email.sendmail("me@mail.com", "you@mail.com", text)
  email.quit()
  return


###Main:
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import requests
import twitter
from datetime import datetime
from bs4 import BeautifulSoup
# Dump the HTML, turn in to BeautifulSoup object, find and save the table
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
    if cross == '\x00':
      cross2 = " "
    else:
      cross2 = " & " + cross + " "
    if savedCallDate != date:
      if savedCallDate != "none":
        storeCall(callDesc)
      callDesc = "[" + calltype + "] " + street + cross2 + "- " + unitid
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
