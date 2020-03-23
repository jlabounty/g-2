# import HTMLSession from requests_html
from requests_html import HTMLSession
 
# create an HTML Session object
session = HTMLSession()
 
# Use the object above to connect to needed webpage
resp = session.get("http://localhost:8787/fts/status")
#resp = session.get("https://finance.yahoo.com/quote/NFLX/options?p=NFLX")
 
# Run JavaScript code on webpage
resp.html.render()
