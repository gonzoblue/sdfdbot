# Import modules
import requests
from bs4 import BeautifulSoup

#Function to print or send out alert on a fully built call
def inciAlert( fullCall ):
  fullCall = fullCall + " (" + str(numUnits) + ") @ " + prevDate
  coolCall = ['Fire', 'CPTR', 'Sdge']
  if any(word in fullCall for word in coolCall):
    print fullCall
  return

# Dump the HTML
print "Starting...\n"
r = requests.get('http://apps.sandiego.gov/sdfiredispatch/')
#r = requests.get('http://localhost/sdfd.html')

# Turn the HTML into a Beautiful Soup object
soup = BeautifulSoup(r.text, 'html.parser')

# Find the calls table and save it
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr("id") and tag['id']=="gv1")

# Variables
prevDate = "none"
callDesc = []

# Run through each row and pick apart the call details
for row in table.findAll("tr"):
  call = row.findAll("td")
  if len(call) == 5: 
    date = str(call[0].get_text().strip())
    type = str(call[1].get_text().strip())
    street = str(call[2].get_text().strip())
    cross = str(call[3].get_text().strip())
    unit = str(call[4].get_text().strip())

# Build the incident string, adding units each time. If a new incident is found, alert/print the call.
    if date != prevDate:
      if prevDate != "none":
        inciAlert(callDesc)
      callDesc = "[" + type + "] " + street + " - " + unit
      numUnits = 1
    else:
      callDesc = callDesc + ", " + unit
      numUnits = numUnits + 1
    prevDate = date
# Alert/print the last call built
inciAlert(callDesc)

print "\nFinished."
exit()
