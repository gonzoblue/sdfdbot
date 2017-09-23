#https://github.com/gonzoblue/sdfdbot
#Automated SDFD pulsepoint scraping and alerting
#Not official or affiliated with SDFD in any way

#Imports
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from secrets import EMAIL_FROM, EMAIL_TO, EMAIL_PASS, EMAIL_SERVER, TWITTER_CONSUMERKEY, TWITTER_CONSUMERSECRET, TWITTER_ACCESSKEY, TWITTER_ACCESSSECRET, COOLCALL, DBPATH
import requests
import twitter
from datetime import datetime
from bs4 import BeautifulSoup
import sqlite3

#Set up the database
callsdb_file = DBPATH + "callsdb.sqlite"
db = sqlite3.connect(callsdb_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS calls (dbid INTEGER PRIMARY KEY, dbcalldate TEXT, dbcalltype TEXT, dbstreet TEXT, dblat REAL, dblong REAL, dbunitids TEXT, dbnumunits INTEGER, dbupdatetime timestamp)')
db.commit()

def storeCall():
	c.execute('SELECT dbid FROM calls WHERE dbcalldate=?', (calldate,)) #search for the call in the DB by dispatch date/time
	thisCall = c.fetchone()
	now = datetime.now()
	if thisCall > 0:  #if call exists in DB
		callChanged = 0
		whatChanged = " \nUpdated:"
		c.execute('SELECT * FROM calls WHERE dbid=?', (thisCall))
		oldEntry = c.fetchone() # save the old DB entry for comparison
		print "=" + str(oldEntry)
		oldCallType = str(oldEntry[2])
		oldAddress = str(oldEntry[3])
		oldLat = float(oldEntry[4])
		oldLong = float(oldEntry[5])
		oldNumUnits = oldEntry[7]
		if oldCallType != calltype: #call exists, check for updated call type
			c.execute('UPDATE calls SET dbcalltype=? where dbid=?', (calltype, thisCall[0]))
			db.commit()
			callChanged=1
			whatChanged = whatChanged + "type "
		if oldAddress != address:
			c.execute('UPDATE calls SET dbstreet=? where dbid=?', (address, thisCall[0]))
			db.commit()
			callChanged=1
			whatChanged = whatChanged + "address "
		if (oldLat != lat) or (oldLong != long):
			c.execute('UPDATE calls SET dblat=? where dbid=?', (lat, thisCall[0]))
			c.execute('UPDATE calls SET dblong=? where dbid=?', (long, thisCall[0]))
			db.commit()
			callChanged = 1
			whatChanged = whatChanged + "lat/long "
		if oldNumUnits != numunits:
			c.execute('UPDATE calls SET dbunitids=? where dbid=?', (unitids, thisCall[0]))
			c.execute('UPDATE calls SET dbnumunits=? where dbid=?', (numunits, thisCall[0]))
			db.commit()
			callChanged=1
			whatChanged = whatChanged + "units "
		if callChanged==1:  #If the call was changed, update the DB
			c.execute('UPDATE calls SET dbupdatetime=? where dbid=?', (now, thisCall[0]))
			db.commit()
			c.execute('SELECT * FROM calls WHERE dbcalldate=?', (calldate,))
			call = c.fetchone()
			print "$" + str(call)
			return 2, str(call[0]) + whatChanged
		else:  #call exists and wasn't updated
			return 0, str(thisCall[0])
	else:  #if this call is new
		c.execute('INSERT INTO calls(dbcalldate, dbcalltype, dbstreet, dblat, dblong, dbunitids, dbnumunits, dbupdatetime) VALUES(?,?,?,?,?,?,?,?)', (calldate, calltype, address, lat, long, unitids, numunits, now))
		db.commit()
		c.execute('SELECT * FROM calls WHERE dbcalldate=?', (calldate,))
		call = c.fetchone()
		print "+" + str(call)
		return 1, str(call[0])
	return -1, "error"

def sendTweet(fullCall):
	tweet = twitter.Api(consumer_key=TWITTER_CONSUMERKEY,consumer_secret=TWITTER_CONSUMERSECRET,access_token_key=TWITTER_ACCESSKEY,access_token_secret=TWITTER_ACCESSSECRET)
	status = tweet.PostUpdate(fullCall)
	print "Tweet sent: " + fullCall
	return

def sendEmail(footer):
	fromaddr = EMAIL_FROM
	toaddr = EMAIL_TO
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject']= "SDFD: " + calltype + " @ " + address + " with " + str(numunits) + " units"
	body = calltype + "\n" + address + "\n" + unitids + " (" + str(numunits) + ")\n@" + calldate + "\nhttp://maps.google.com/?q=" + str(lat) + "," + str(long) + "\n\n--\nDBID: " + footer
	msg.attach(MIMEText(body, 'plain'))
	email = smtplib.SMTP(EMAIL_SERVER, 587)
	email.ehlo()
	email.starttls()
	email.ehlo()
	email.login(EMAIL_FROM,EMAIL_PASS)
	text = msg.as_string()
	email.sendmail(EMAIL_FROM, EMAIL_TO, text)
	email.quit()
	print "Emailed: " + calltype + " @ " + calldate
	return

###Main:
r = requests.get('https://webapp.pulsepoint.org/active_incidents.php?agencyid=37140&tz=420')
soup = BeautifulSoup(r.text, 'html.parser')
#callDesc = " "

for row in soup.findAll("row"):  # Run through each row and pick apart the call details
	call = row.findAll("cell")
	if len(call) == 6:  #If the row contains probably good call data
		calldate = str(call[0].get_text())
		calltype = str(call[5].get_text())
		address = str(call[2].get_text())
		address = address.split(", SAN DIEGO", 1)[0]
		unitids = BeautifulSoup(call[3].get_text(), 'html.parser')
		unitids = str(unitids.get_text())
		unitids = unitids.replace("?", "")
		unitids = unitids.replace("^", "")
		latlong = str(call[4].get_text())
		lat = float(latlong.split(',')[0])
		long = float(latlong.split(',')[1])
		numunits = unitids.count(',') + 1
		callDesc = "[" + calltype + "] " + address + ": " + unitids + " (" + str(numunits) + ") @ " + calldate + " http://maps.google.com/?q=" + str(lat) + "," + str(long)
		savedType,savedFooter = storeCall() #Store the call. Reutrn type is 0 for old, 1 for new, 2 for update call. Footer is a string of dbid & what (if any) changed
		if savedType == 1:  #If it is a new call
			sendTweet(callDesc)
		if savedType > 0:  #If the call is new or updated
			if numunits > 7 or any(word in callDesc for word in COOLCALL):  #Check if it should email
				sendEmail(savedFooter)
		elif savedType < 0:
			sendEmail("\nstoreCall() ERROR!!")
			print "storeCall() ERROR!!"
			exit()
print "\nFinished."
exit()
