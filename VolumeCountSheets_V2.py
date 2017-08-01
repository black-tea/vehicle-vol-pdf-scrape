import sys
import csv
import glob

# Currently all the packages are being installed in the anaconda distribution of python
# so this append process just adds the paths to those packages for this one
# new_path = ['', '/home/tcblack/anaconda2/lib/python27.zip', '/home/tcblack/anaconda2/lib/python2.7', '/home/tcblack/anaconda2/lib/python2.7/plat-linux2', '/home/tcblack/anaconda2/lib/python2.7/lib-tk', '/home/tcblack/anaconda2/lib/python2.7/lib-old', '/home/tcblack/anaconda2/lib/python2.7/lib-dynload', '/home/tcblack/anaconda2/lib/python2.7/site-packages', '/home/tcblack/anaconda2/lib/python2.7/site-packages/Sphinx-1.5.1-py2.7.egg', '/home/tcblack/anaconda2/lib/python2.7/site-packages/setuptools-27.2.0-py2.7.egg']
# for i in new_path:
#     sys.path.append(i)

from datetime import datetime, date, time
import pdfquery

# Need two items
# 1) A folder of all the pdfs
# 2) A csv that contains the file name and the associated cl_node_id (currently on NavLA)


# Loop through all the CSVs. Try the file: if error 
# Also create a new csv that keeps track of the status of each one return 1 for complete, 0 for error

folder = 'TrafficCountData/Manual Counts-20170526T005814Z-001/Manual Counts/'
filename = '2ND.48TH.150611-NDSMAN.pdf'
path = folder + filename


def pdf_extract(path):

    # Load the PDF
    pdf = pdfquery.PDFQuery(path,resort=False)
    pdf.load()

    #hi = pdf.tree.write(path,pretty_print=True)
    #exit()

    # Create Empty Dict to organize the output
    Manual_TC = {}

    ##### Survey Information
    # Begin with reference points

    LabelList = ["North/South",
                 'East/West',
                 'Day:','Date:',
                 'Weather:',
                 'Hours:',
                 'School Day:',
                 'District:',
                 'I/S CODE',
                 'WHEELED',
                 'BIKES',
                 'BUSES',
                 'N/B TIME',
                 'S/B TIME',
                 'E/B TIME',
                 'W/B TIME',
                 #'survey_hours'
                 'NORTHBOUND Approach',
                 'SOUTHBOUND Approach',
                 'EASTBOUND Approach',
                 'WESTBOUND Approach',
                 'XING S/L',
                 'XING N/L',
                 'XING W/L',
                 'XING E/L']
    
    Offsets = {}
    Offsets['North/South'] = [70,-5,350,15]
    Offsets['East/West'] = [70,-5,350,15]
    Offsets['Day:'] = [5,-5,120,15]
    Offsets['Date:'] = [30,-8,130,15]
    Offsets['Weather:'] = [30,-8,130,15]
    Offsets['Hours:'] = [30,-8,130,15]
    Offsets['School Day:'] = [40,-5,120,15]
    Offsets['District:'] = [40,-5,130,15]
    #Offsets['I/S CODE']
    Offsets['WHEELED'] = [70,-30,380,12]
    Offsets['N/B TIME'] = {}
    Offsets['S/B TIME'] = {}
    Offsets['E/B TIME'] = {}
    Offsets['W/B TIME'] = {}
    Offsets['N/B TIME']['vol'] = [-5,-91,18,-1]
    Offsets['N/B TIME']['time'] = [18,-91,55,-1]
    Offsets['S/B TIME']['vol'] = [-5,-91,18,-1]
    Offsets['S/B TIME']['time'] = [18,-91,55,-1]
    Offsets['E/B TIME']['vol'] = [-5,-91,18,-1]
    Offsets['E/B TIME']['time'] = [18,-91,55,-1]
    Offsets['W/B TIME']['vol'] = [-5,-91,18,-1]
    Offsets['W/B TIME']['time'] = [18,-91,55,-1]
    Offsets['survey_hours'] = [-2,-101,23,-15] # These offset values are based on the lower left corner of 'NORTHBOUND Approach'
    Offsets['NORTHBOUND Approach'] = [43,-95,135,-19]
    Offsets['SOUTHBOUND Approach'] = [43,-95,135,-19]
    Offsets['EASTBOUND Approach'] = [43,-95,135,-19]
    Offsets['WESTBOUND Approach'] = [43,-95,135,-19]
    Offsets['XING S/L'] = [-5,-85,45,-15]
    Offsets['XING N/L'] = [-5,-85,45,-15]
    Offsets['XING W/L'] = [-5,-85,45,-15]
    Offsets['XING E/L'] = [-5,-85,45,-15]

    ##### Get coords for Lt, Th, Rt Objects
    movements = ['Lt','Th ','Rt']
    direction_coords = {}
    for movement in movements:
        direction_coords[movement] = {}
        List_x = []
        List_y = []
        search = pdf.pq('LTTextLineHorizontal:contains("%s")' % (movement))

        # For each LTTextLineHorizontal Object, get Bounding box. Search "LTTetLineHorizontal" on https://github.com/euske/pdfminer/blob/master/pdfminer/layout.py
        for instance in search:
            List_x.append(instance.layout.bbox[0])
            List_y.append(instance.layout.bbox[1])
        direction_coords[movement]['NB'] = [round(min(List_x),2),round(max(List_y),2)]
        direction_coords[movement]['SB'] = [round(max(List_x),2),round(max(List_y),2)]
        direction_coords[movement]['EB'] = [round(min(List_x),2),round(min(List_y),2)]
        direction_coords[movement]['WB'] = [round(max(List_x),2),round(min(List_y),2)]
    #print direction_coords



    Label_coords = {}

    for label in LabelList:
        #print label
        Label_coords[label] = {}
        Label_grab = pdf.pq('LTTextLineHorizontal:contains("%s")' % (label))
        Label_coords[label]['x0y0'] = {}
        Label_coords[label]['x0y0']['x0'] = float(Label_grab.attr('x0'))
        Label_coords[label]['x0y0']['y0'] = float(Label_grab.attr('y0'))
        Label_coords[label]['x1y1'] = {}
        Label_coords[label]['x1y1']['x1'] = float(Label_grab.attr('x1'))
        Label_coords[label]['x1y1']['y1'] = float(Label_grab.attr('y1'))

        if label in ('N/B TIME','S/B TIME','E/B TIME','W/B TIME'):
            #print "testing label grab"
            #print Label_grab
            try:
                for key in Offsets[label]:
                    Label_coords[label][key] = {}
                    Label_coords[label][key]['box_coords'] = [Offsets[label][key][0] + Label_coords[label]['x0y0']['x0'],
                                                              Offsets[label][key][1] + Label_coords[label]['x0y0']['y0'],
                                                              Offsets[label][key][2] + Label_coords[label]['x0y0']['x0'],
                                                              Offsets[label][key][3] + Label_coords[label]['x0y0']['y0']
                                                              ]
            except:
                pass
        else:
            try:
                Label_coords[label]['box_coords'] = [Offsets[label][0] + Label_coords[label]['x0y0']['x0'],
                                                     Offsets[label][1] + Label_coords[label]['x0y0']['y0'],
                                                     Offsets[label][2] + Label_coords[label]['x0y0']['x0'],
                                                     Offsets[label][3] + Label_coords[label]['x0y0']['y0']
                                                     ]
            except:
                pass
    
    ##### Set parameters for Peak Hour / 15 Min Counts

    # Grab the X value immediately to the right of MIN
    min_grab = pdf.pq('LTTextLineHorizontal:contains("MIN")')
    List_y = []
    for instance in min_grab:
        # Grab the right-side (x value) of the instance of min
        List_x.append(instance.layout.bbox[2])
    min_x_coord = min(List_x)

    # Bounding box for the Totals
    total_grab = pdf.pq('LTTextLineHorizontal:contains("TOTAL")')
    total_grab_coords = []
    #print "TOTAL GRABBBBB"
    for instance in total_grab:
        # Grab the top right corner of each instance
        total_grab_coords.append([instance.layout.bbox[2], instance.layout.bbox[3]])
    total_coords = {}
    Label_coords['TOTAL'] = {}
    #print total_grab_coords
    for coord in total_grab_coords:
        if (coord[0] < Label_coords["NORTHBOUND Approach"]['x1y1']['x1']) & (coord[1] > Label_coords["EASTBOUND Approach"]['x1y1']['y1']):
            Label_coords['TOTAL']['NB'] = [coord[0], coord[1]]
        elif (coord[0] < Label_coords["NORTHBOUND Approach"]['x1y1']['x1']) & (coord[1] < Label_coords["EASTBOUND Approach"]['x1y1']['y1']):
            Label_coords['TOTAL']['EB'] = [coord[0], coord[1]]
        elif (coord[0] > Label_coords["NORTHBOUND Approach"]['x1y1']['x1']) & (coord[1] > Label_coords["EASTBOUND Approach"]['x1y1']['y1'] + 5):
            Label_coords['TOTAL']['SB'] = [coord[0], coord[1]]
        elif (coord[0] > Label_coords["NORTHBOUND Approach"]['x1y1']['x1']) & (coord[1] < Label_coords["EASTBOUND Approach"]['x1y1']['y1']):
            Label_coords['TOTAL']['WB'] = [coord[0], coord[1]]
    #print "totalnb"
    #print Label_coords['TOTAL']['NB']
    #print "totaleb"
    #print Label_coords['TOTAL']['EB']
    #print "totalsb"
    #print Label_coords['TOTAL']['SB']
    #print "totalwb"
    #print Label_coords['TOTAL']['WB']
    #exit()

    ##### Get coords for Ped, Sch objects

    # Begin for searching where Ped and Sch are one object; 
    # if that does not work, move to searching for both individually
    try:
        ped_types = ['Ped Sch']
        ped_coords = {}
        for ped_type in ped_types:
            #print ped_type
            ped_coords[ped_type] = {}
            List_x0 = []
            List_y0 = []
            List_x1 = []
            List_y1 = []
            search = pdf.pq('LTTextLineHorizontal:contains("%s")' % (ped_type))
            #print search

            # For each, get coordinates of bottom-right corner
            for instance in search:
                List_x0.append(instance.layout.bbox[0])
                List_y0.append(instance.layout.bbox[1])
                List_x1.append(instance.layout.bbox[2])
                List_y1.append(instance.layout.bbox[3])
            
            
            ped_coords[ped_type]['S/L'] = [round(min(List_x0),2), round(max(List_y0),2), round(min(List_x1),2), round(max(List_y1),2)]
            ped_coords[ped_type]['N/L'] = [round(max(List_x0),2), round(max(List_y0),2), round(max(List_x1),2), round(max(List_y1),2)]
            ped_coords[ped_type]['W/L'] = [round(min(List_x0),2), round(min(List_y0),2), round(min(List_x1),2), round(min(List_y1),2)]
            ped_coords[ped_type]['E/L'] = [round(max(List_x0),2), round(min(List_y0),2), round(max(List_x1),2), round(min(List_y1),2)]
        

        Label_coords['Ped'] = {}
        Label_coords['Sch'] = {}

        Label_coords['Ped']['S/L'] = [ped_coords['Ped Sch']['S/L'][0]-5,
                                      Label_coords['TOTAL']['SB'][1],
                                      ((ped_coords['Ped Sch']['S/L'][2]-ped_coords['Ped Sch']['S/L'][0])/2+ped_coords['Ped Sch']['S/L'][0]),
                                      ped_coords['Ped Sch']['S/L'][1]+2
                                      ]
        
        Label_coords['Sch']['S/L'] = [((ped_coords['Ped Sch']['S/L'][2]-ped_coords['Ped Sch']['S/L'][0])/2+ped_coords['Ped Sch']['S/L'][0]),
                                      Label_coords['TOTAL']['SB'][1],
                                      ped_coords['Ped Sch']['S/L'][2]+5,
                                      ped_coords['Ped Sch']['S/L'][1]+2
                                      ]

        Label_coords['Ped']['N/L'] = [ped_coords['Ped Sch']['N/L'][0]-5,
                                      Label_coords['TOTAL']['SB'][1],
                                      ((ped_coords['Ped Sch']['N/L'][2]-ped_coords['Ped Sch']['N/L'][0])/2+ped_coords['Ped Sch']['N/L'][0]),
                                      ped_coords['Ped Sch']['N/L'][1]+2
                                      ]

        Label_coords['Sch']['N/L'] = [((ped_coords['Ped Sch']['N/L'][2]-ped_coords['Ped Sch']['N/L'][0])/2+ped_coords['Ped Sch']['N/L'][0]),
                                      Label_coords['TOTAL']['SB'][1],
                                      ped_coords['Ped Sch']['N/L'][2]+5,
                                      ped_coords['Ped Sch']['N/L'][1]+2
                                      ]

        Label_coords['Ped']['W/L'] = [ped_coords['Ped Sch']['W/L'][0]-5,
                                      Label_coords['TOTAL']['WB'][1],
                                      ((ped_coords['Ped Sch']['W/L'][2]-ped_coords['Ped Sch']['W/L'][0])/2+ped_coords['Ped Sch']['W/L'][0]),
                                      ped_coords['Ped Sch']['W/L'][1]+2
                                      ]
        
        Label_coords['Sch']['W/L'] = [((ped_coords['Ped Sch']['W/L'][2]-ped_coords['Ped Sch']['W/L'][0])/2+ped_coords['Ped Sch']['W/L'][0]),
                                      Label_coords['TOTAL']['WB'][1],
                                      ped_coords['Ped Sch']['W/L'][2]+5,
                                      ped_coords['Ped Sch']['W/L'][1]+2
                                      ]

        Label_coords['Ped']['E/L'] = [ped_coords['Ped Sch']['E/L'][0]-5,
                                      Label_coords['TOTAL']['WB'][1],
                                      ((ped_coords['Ped Sch']['E/L'][2]-ped_coords['Ped Sch']['E/L'][0])/2+ped_coords['Ped Sch']['E/L'][0]),
                                      ped_coords['Ped Sch']['E/L'][1]+2
                                      ]
        
        Label_coords['Sch']['E/L'] = [((ped_coords['Ped Sch']['E/L'][2]-ped_coords['Ped Sch']['E/L'][0])/2+ped_coords['Ped Sch']['E/L'][0]),
                                      Label_coords['TOTAL']['WB'][1],
                                      ped_coords['Ped Sch']['E/L'][2]+5,
                                      ped_coords['Ped Sch']['E/L'][1]+2
                                      ]
    except:
        #print "trying"
        # Now try it with 'Ped' and 'Sch' separate
        try:

            ped_types = ['Ped', 'Sch ']
            ped_coords = {}
            for ped_type in ped_types:
                #print ped_type
                ped_coords[ped_type] = {}
                List_x0 = []
                List_y0 = []
                List_x1 = []
                List_y1 = []
                search = pdf.pq('LTTextLineHorizontal:contains("%s")' % (ped_type))

                # For each, get the bounding box coordinates
                for instance in search:
                    List_x0.append(instance.layout.bbox[0])
                    List_y0.append(instance.layout.bbox[1])
                    List_x1.append(instance.layout.bbox[2])
                    List_y1.append(instance.layout.bbox[3])
                
                
                ped_coords[ped_type]['S/L'] = [round(min(List_x0),2), round(max(List_y0),2), round(min(List_x1),2), round(max(List_y1),2)]
                ped_coords[ped_type]['N/L'] = [round(max(List_x0),2), round(max(List_y0),2), round(max(List_x1),2), round(max(List_y1),2)]
                ped_coords[ped_type]['W/L'] = [round(min(List_x0),2), round(min(List_y0),2), round(min(List_x1),2), round(min(List_y1),2)]
                ped_coords[ped_type]['E/L'] = [round(max(List_x0),2), round(min(List_y0),2), round(max(List_x1),2), round(min(List_y1),2)]

            Label_coords['Ped'] = {}
            Label_coords['Sch'] = {}

            Label_coords['Ped']['S/L'] = [ped_coords['Ped']['S/L'][0]-5,
                                          Label_coords['TOTAL']['SB'][1],
                                          ped_coords['Ped']['S/L'][2]+2,
                                          ped_coords['Ped']['S/L'][1]+2
                                          ]
            
            Label_coords['Sch']['S/L'] = [ped_coords['Ped']['S/L'][2],
                                          Label_coords['TOTAL']['SB'][1],
                                          ped_coords['Sch ']['S/L'][2]+5,
                                          ped_coords['Sch ']['S/L'][1]+2
                                          ]

            Label_coords['Ped']['N/L'] = [ped_coords['Ped']['N/L'][0]-5,
                                          Label_coords['TOTAL']['SB'][1],
                                          ped_coords['Ped']['N/L'][2]+2,
                                          ped_coords['Ped']['N/L'][1]+2
                                          ]

            Label_coords['Sch']['N/L'] = [ped_coords['Ped']['N/L'][2],
                                          Label_coords['TOTAL']['SB'][1],
                                          ped_coords['Sch ']['N/L'][2]+5,
                                          ped_coords['Sch ']['N/L'][1]+2
                                          ]

            Label_coords['Ped']['W/L'] = [ped_coords['Ped']['W/L'][0]-5,
                                          Label_coords['TOTAL']['WB'][1],
                                          ped_coords['Ped']['W/L'][2]+2,
                                          ped_coords['Ped']['W/L'][1]+2
                                          ]
            
            Label_coords['Sch']['W/L'] = [ped_coords['Ped']['W/L'][2],
                                          Label_coords['TOTAL']['WB'][1],
                                          ped_coords['Sch ']['W/L'][2]+5,
                                          ped_coords['Sch ']['W/L'][1]+2
                                          ]

            Label_coords['Ped']['E/L'] = [ped_coords['Ped']['E/L'][0]-5,
                                          Label_coords['TOTAL']['WB'][1],
                                          ped_coords['Ped']['E/L'][2]+2,
                                          ped_coords['Ped']['E/L'][1]+2
                                          ]
            
            Label_coords['Sch']['E/L'] = [ped_coords['Ped']['E/L'][2],
                                          Label_coords['TOTAL']['WB'][1],
                                          ped_coords['Sch ']['E/L'][2]+5,
                                          ped_coords['Sch ']['E/L'][1]+2
                                          ]

        except:

            pass




    #print Label_coords['Sch']
    #print Label_coords['Ped']
    #print "ending!!"
    #exit()


    # All possible labels
    peak_labels = ['N/B TIME','S/B TIME','E/B TIME','W/B TIME']
    dir_coords = {}
    # Find the location of each in the document
    for label in peak_labels:
        label_grab = pdf.pq('LTTextLineHorizontal:contains("%s")' % (label))
        # Grab the bottom right corner of 'TIME'
        dir_coords[label] = [float(label_grab.attr('x1')),float(label_grab.attr('y0'))]
        # Grab the location of the direction (minus 'TIME') to create a line that will split the volume from the times
        dir_label = label[:-5] 
        dir_grab = pdf.pq('LTTextLineHorizontal:contains("%s")' % (dir_label))
        List_x = []
        List_y = []
        # For each instance of each direction, grab the coordinates of the bottom-right corner
        for instance in dir_grab:
            List_x.append(instance.layout.bbox[2])
            List_y.append(instance.layout.bbox[1])
        # We want to grab the instance that is lower (not for the special vehicles, but for the peak periods)
        dir_coords[dir_label] = [round(min(List_x),2),round(min(List_y),2)]
    #print dir_coords

    Label_coords['pk'] = {}
    Label_coords['pk']['nbvol'] = [min_x_coord, Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5, dir_coords["N/B"][0]+2, dir_coords["N/B"][1]]
    Label_coords['pk']['nbtime'] = [dir_coords["N/B"][0], Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5, dir_coords["N/B TIME"][0]+5,dir_coords["N/B TIME"][1]]

    Label_coords['pk']['sbvol'] = [dir_coords["N/B TIME"][0]+2, Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5,dir_coords["S/B"][0]+5, dir_coords["S/B"][1]]
    Label_coords['pk']['sbtime'] = [dir_coords["S/B"][0], Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5, dir_coords["S/B TIME"][0]+5,dir_coords["S/B TIME"][1]]

    Label_coords['pk']['ebvol'] = [dir_coords["S/B TIME"][0]+2, Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5,dir_coords["E/B"][0]+5, dir_coords["E/B"][1]]
    Label_coords['pk']['ebtime'] = [dir_coords["E/B"][0], Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5, dir_coords["E/B TIME"][0]+5,dir_coords["E/B TIME"][1]]

    Label_coords['pk']['wbvol'] = [dir_coords["E/B TIME"][0]+2, Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5,dir_coords["W/B"][0]+5, dir_coords["W/B"][1]]
    Label_coords['pk']['wbtime'] = [dir_coords["W/B"][0], Label_coords["NORTHBOUND Approach"]['x0y0']['y0']+5, dir_coords["W/B TIME"][0]+5,dir_coords["W/B TIME"][1]]

    #for key in Label_coords['pk']:
        #print key
        #print Label_coords['pk'][key]
    #exit()

    # Bounding box for the Hours Field
    hours_search = pdf.pq('LTTextLineHorizontal:contains("Hours ")')
    List_x = []
    List_y = []
    for instance in hours_search:
        List_x.append(instance.layout.bbox[0])
        List_y.append(instance.layout.bbox[1])
    hours_coords = [round(min(List_x),2),round(max(List_y),2)]

    Label_coords['survey_hours'] = {}
    Label_coords['survey_hours']['box_coords'] = [-5 + hours_coords[0],
                              Label_coords['TOTAL']['NB'][1],
                              direction_coords['Lt']['NB'][0],
                              direction_coords['Lt']['NB'][1] + 3
                              ]
    
    # Bounding boxes for the Main Volume Data
    directions = ['NB','SB','EB','WB']
    for direction in directions:
        Label_coords[direction] = {}
        Label_coords[direction]['Rt'] = [direction_coords['Rt'][direction][0], Label_coords['TOTAL'][direction][1] + 1, direction_coords['Rt'][direction][0] + 22, direction_coords['Rt'][direction][1] + 2]
        Label_coords[direction]['Th'] = [direction_coords['Th '][direction][0], Label_coords['TOTAL'][direction][1] + 1, direction_coords['Rt'][direction][0]+1, direction_coords['Th '][direction][1] +2]
        Label_coords[direction]['Lt'] = [direction_coords['Lt'][direction][0], Label_coords['TOTAL'][direction][1] + 1, direction_coords['Th '][direction][0], direction_coords['Lt'][direction][1] + 2]


    ##### Survey Information
    survey_info = pdf.extract([
        ('with_formatter','text'),
        ('street_ns', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['North/South']['box_coords']))),
        ('street_ew', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['East/West']['box_coords']))),
        ('dayofweek', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Day:']['box_coords']))),
        ('date', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Date:']['box_coords']))),
        ('weather', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Weather:']['box_coords']))),
        ('hours', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Hours:']['box_coords']))),
        ('school_day', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['School Day:']['box_coords']))),
        ('district', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['School Day:']['box_coords']))),
        ])

    # TESTING
    #print "survey info"
    #print survey_info

    # Reformat date, add to Manual_TC
    #print survey_info
    survey_info['date'] = datetime.strptime(survey_info['date'], '%B %d, %Y').date()
    Manual_TC['Info'] = survey_info

    ##### Special Vehicles: Dual-Wheeled, Bikes, Buses
    # Initial data grab
    special_veh_scrape = pdf.extract([
        ('with_formatter','text'),
        ('data', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['WHEELED']['box_coords'])))
        ])
    special_veh_scrape = special_veh_scrape['data'].split()
    special_veh_dict = {}
    special_veh_dict['NB'] = special_veh_scrape[0:3] 
    special_veh_dict['SB'] = special_veh_scrape[3:6]
    special_veh_dict['EB'] = special_veh_scrape[6:9]
    special_veh_dict['WB'] = special_veh_scrape[9:12]
    special_veh_list = ['dual','bike','bus']

    # Final list of dictionaries
    special_vehicles = []
    for direction in special_veh_dict:
        for i in range(0,len(special_veh_dict[direction])):
            temp_dict = {}
            temp_dict['approach'] = direction
            temp_dict['type'] = special_veh_list[i]
            temp_dict['volume'] = special_veh_dict[direction][i]
            special_vehicles.append(temp_dict)

    # Append to Manual_TC
    Manual_TC['Spec_Veh'] = special_vehicles

    ##### Peak Counts
    peak_types = ['am15','pm15','am60','pm60']
    directions = ['NB','EB','WB','SB']


    peak_time_scrape = pdf.extract([
        ('with_formatter','text'),
        ('NB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['nbtime']))),
        ('SB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['sbtime']))),
        ('EB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['ebtime']))),
        ('WB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['wbtime'])))
        ])

    peak_vol_scrape = pdf.extract([
        ('with_formatter','text'),
        ('NB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['nbvol']))),
        ('SB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['sbvol']))),
        ('EB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['ebvol']))),
        ('WB', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['pk']['wbvol'])))
        ])

    peak_direction = []

    for direction in directions:
        
        peak_dict = {}    
        peak_time_split = peak_time_scrape[direction].split()
        peak_vol_split = peak_vol_scrape[direction].split()

        for i in range(0,len(peak_time_split)): #COME BACK AND CHECK LATER

            peak_dict['type'] = peak_types[i]
            peak_dict['approach'] = direction
            peak_dict['time'] = peak_time_split[i]
            peak_dict['volume'] = peak_vol_split[i]
        peak_direction.append(peak_dict)

    # Append to Manual_TC
    Manual_TC['PeakVol'] = peak_direction

    ##### Survey Hours (offsets based on 'NORTHBOUND Approach label')
    survey_hours = pdf.extract([
        ('with_formatter','text'),
        ('hours', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['survey_hours']['box_coords'])))
        ])
    survey_hours['hours'] = survey_hours['hours'].split()

    #Format survey hours using strptime
    for i in range(0, len(survey_hours['hours'])):
        hoursplit = survey_hours['hours'][i].split('-')
        for fmt in ('%H','%H:%M'):
            try:
                starttime = datetime.strptime(hoursplit[0],fmt)
                endtime = datetime.strptime(hoursplit[1],fmt)
            except ValueError:
                pass
        starttime = datetime.combine(survey_info['date'], starttime.time())
        endtime = datetime.combine(survey_info['date'], endtime.time())
        survey_hours['hours'][i] = [starttime, endtime]

    ##### Volume Data
    volume_scrape = {}

    volume_extract = {}
    movements = ['Lt','Th','Rt']
    for direction in directions:
        volume_extract[direction] = {}

        for movement in movements:
            coords = Label_coords[direction][movement]

            if movement == 'Th':
                extract = pdf.extract([
                    ('with_formatter','text'),
                    ('test','LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in coords)))
                    ])
            
            else:
                extract = pdf.extract([
                    ('with_formatter','text'),
                    ('test','LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in coords)))
                    ])
            volume_extract[direction][movement] = extract['test'].split()


    # Final list of dictionaries
    volume_data = []
    for direction in volume_extract:
        for movement in volume_extract[direction]:
            for i in range(0,len(volume_extract[direction][movement])):
                empty_dict = {}
                #print volume_extract[direction][movement][i]
                empty_dict['approach'] = direction
                empty_dict['movement'] = movement
                empty_dict['start_time'] = survey_hours['hours'][i][0]
                empty_dict['end_time'] = survey_hours['hours'][i][1]
                empty_dict['volume'] = volume_extract[direction][movement][i]
                volume_data.append(empty_dict)

    # Append to Manual_TC
    Manual_TC['Volume'] = volume_data

    ##### Ped / Schoolchildren Volume Data
    # Initial Data Grab
    ped_scrape = pdf.extract([
        ('with_formatter','text'),
        ('SL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Ped']['S/L']))),
        ('NL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Ped']['N/L']))),
        ('WL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Ped']['W/L']))),
        ('EL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Ped']['E/L'])))
        ])
    
    sch_scrape = pdf.extract([
        ('with_formatter','text'),
        ('SL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Sch']['S/L']))),
        ('NL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Sch']['N/L']))),
        ('WL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Sch']['W/L']))),
        ('EL', 'LTTextLineHorizontal:in_bbox("%s")' % (','.join(str(e) for e in Label_coords['Sch']['E/L'])))
    ])

    # Split Ped v. Sch
    ped_sch_extract = {}
    legs = ['SL','NL','WL','EL']
    for leg in legs:
        ped_sch_extract[leg] = {}
        ped_sch_extract[leg]['Ped'] = ped_scrape[leg].split()
        ped_sch_extract[leg]['Sch'] = sch_scrape[leg].split()


    # Assign it to hour
    ped_sch_data = []
    for leg in ped_sch_extract:
        for pedtype in ped_sch_extract[leg]:
            for i in range(0,len(ped_sch_extract[leg][pedtype])):
                ped_sch_dict = {}
                ped_sch_dict['xing_leg'] = leg
                ped_sch_dict['type'] = pedtype
                ped_sch_dict['start_time'] = survey_hours['hours'][i][0]
                ped_sch_dict['end_time'] = survey_hours['hours'][i][1]
                ped_sch_dict['volume'] = ped_sch_extract[leg][pedtype][i]
                ped_sch_data.append(ped_sch_dict)

    # Append to Manual_TC
    Manual_TC['Pedestrian'] = ped_sch_data

    ##### Return Final Dict
    print "success!"
    return Manual_TC


