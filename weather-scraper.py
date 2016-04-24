"""
Example script that scrapes data from the IEM ASOS download service
"""
import json
import datetime
import urllib.request, urllib.error, urllib.parse

# timestamps in UTC to request data for
startts = datetime.datetime(2016, 1, 1)
endts = datetime.datetime(2016, 2, 1)

SERVICE = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
SERVICE += "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

SERVICE += startts.strftime('year1=%Y&month1=%m&day1=%d&')
SERVICE += endts.strftime('year2=%Y&month2=%m&day2=%d&')

states = """AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME
 MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT
 WA WI WV WY"""
# IEM quirk to have Iowa AWOS sites in its own labeled network
networks = ['AWOS']
for state in states.split():
    networks.append("%s_ASOS" % (state,))

for network in networks:
    # Get metadata
    uri = "http://mesonet.agron.iastate.edu/geojson/network.php?network=%s" % (
                                                                    network,)
    data = urllib.request.urlopen(uri)
    b = data.read()
    jdict = json.loads(b.decode('utf-8'))
    for site in jdict['features']:
        faaid = site['properties']['sid']
        sitename = site['properties']['sname']
        uri = '%s&station=%s' % (SERVICE, faaid)
        print('Network: %s Downloading: %s [%s]' % (network, sitename, faaid))
        data = urllib.request.urlopen(uri)
        outfn = '%s_%s_%s.txt' % (faaid, startts.strftime("%Y%m%d%H%M"),
                                  endts.strftime("%Y%m%d%H%M"))
        out = open(outfn, 'w')
        out.write(str(data.read(), encoding='utf-8'))
        out.close()
