# Import modules
import requests
from bs4 import BeautifulSoup

# Dump the HTML
r = requests.get('http://apps.sandiego.gov/sdfiredispatch/')
# Turn the HTML into a Beautiful Soup object
soup = BeautifulSoup(r.text, 'html.parser')

# Find the calls table and save it
table = soup.find(lambda tag: tag.name=='table' and tag.has_attr("id") and tag['id']=="gv1")

# Run through each row and pick apart the call details
for row in table.findAll("tr"):
  call = row.findAll("td")
  if len(call) == 5: 
    date = call[0].get_text().strip()
    type = call[1].get_text().strip()
    street = call[2].get_text().strip()
    cross = call[3].get_text().strip()
    unit = call[4].get_text().strip()
    print type, "with", unit 
