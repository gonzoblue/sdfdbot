#
#https://github.com/gonzoblue/sdfdbot
#Automated SDFD incident page scraping and alerting
#Not official or affiliated with SDFD in any way
#

# Import modules
import requests
from bs4 import BeautifulSoup

#Function to alert on a fully built interesting call
def inciAlert( fullCall ):
  fullCall = fullCall + " (" + str(numUnits) + ") @ " + prevDate
  coolCall = ['Fire', 'CPTR', 'Sdge']
  if any(word in fullCall for word in coolCall):
    print fullCall
  elif numUnits > 9:
    print fullCall
  else:
    print  "--" + fullCall
  return

# Dump the HTML, turn in to BeautifulSoup object, find and save the table
print "Starting...\n"
r = requests.get('http://apps.sandiego.gov/sdfiredispatch/')
#r = requests.get('http://localhost/sdfd.html')
soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr("id") and tag['id']=="gv1")

# Variables
prevDate = "none"
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

# Build the incident string, adding units each time. If a new incident is found, alert/print the call.
    if date != prevDate:
      if prevDate != "none":
        inciAlert(callDesc)
      callDesc = "[" + calltype + "] " + street + " - " + unitid
      numUnits = 1
    else:
      callDesc = callDesc + ", " + unitid
      numUnits = numUnits + 1
    prevDate = date
# Alert/print the last call built
inciAlert(callDesc)

print "\nFinished."
exit()
