from lxml import html, etree
import requests
import time
import json

Count_data = []

# Base URL to use for the web scraping
base_url = "http://boemaps.eng.ci.la.ca.us/reports/dot_traffic_data_report.cfm?trafficid="

# Loop through integers, grab all data in range
for i in range(1,6):
    time.sleep(.1)
    print i
    d = {}
    # Make the request
    url = base_url + str(i)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    
    # Parse the data
    table_info = tree.xpath('//td[@class="tablerecord"]/text()')
    if len(table_info) > 0:

        # Parse the Node ID
        node_id = tree.xpath('//td[@class="tablerecord"]/text()')[0]
        node_id = node_id.replace(u'\xa0', u'')

        # Parse the Intersection Name
        intersection = tree.xpath('//td[@class="tablerecord"]/text()')[1]
        intersection = intersection.replace(u'\r\n\t\t\t\t\r\n\t\t\t\t\t', u'')
        intersection = intersection.replace(u'\xa0\r\n\t\t\t\t\r\n\t\t\t',u'')

        ##### Automatic Counts
        # Select the table that contains the automatic counts
        automatic_count_table = tree.xpath('//b[text()="Automatic Count"]/../../..')

        # If there is at least automatic count PDF, grab filenames
        if len(automatic_count_table) > 0:
            automatic_count_table = etree.XML(etree.tostring(automatic_count_table[0]))
            automatic_count_pdfs = automatic_count_table.xpath('//a/text()')
            #print automatic_count_pdfs
            d['automatic'] = automatic_count_pdfs
        else:
            d['automatic'] = []

        ##### Manual Counts
        # Select the table that contains manual counts
        manual_count_table = tree.xpath('//b[text()="Manual Count"]/../../..')

        # If there is at least manual count PDF, grab filenames
        if len(manual_count_table) > 0:
            manual_count_table = etree.XML(etree.tostring(manual_count_table[0]))
            manual_count_pdfs = manual_count_table.xpath('//a/text()')
            #print manual_count_pdfs
            d['manual'] = manual_count_pdfs
        else:
            d['manual'] = []

            #for j in automatic_count_table:
                #print etree.tostring(j)

        d['node_id'] = node_id
        d['intersection'] = intersection
        Count_data.append(d)

with open('Z:/VisionZero/GIS/Projects/LADOT_TrafficCounts/navLAdump.txt', 'w') as outfile:
    json.dump(Count_data, outfile)

    # Verify
print(Count_data)
