# Import modules
import requests
from bs4 import BeautifulSoup

#Function to print or send out alert on a full call
def inciAlert( fullCall ):
  print fullCall
  return

# Dump the HTML
##r = requests.get('http://apps.sandiego.gov/sdfiredispatch/')
r = requests.get('http://10.1.1.242/sdfd.html')
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
	callDesc = callDesc + " @ " + prevDate
        inciAlert(callDesc)
      callDesc = "[" + type + "] " + unit
    else:
      callDesc = callDesc + " & " + unit
    prevDate = date
# Alert/print the last call built
inciAlert(callDesc)

print "\nFinished."
exit()
