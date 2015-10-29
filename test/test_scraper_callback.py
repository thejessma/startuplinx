import urllib
import urllib2
import json

url = 'http://localhost:5000/scraper_callback/1'

data = {   
        'name': 'memsql',
        'linkedin_id': 2220441,
        'remote_id': 456456
    }

data = urllib.urlencode({'data': json.dumps(data)})
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
html = response.read()

print html
