import pdfquery
from datetime import datetime, date, time

# Need two items
# 1) A folder of all the pdfs
# 2) A csv that contains the file name and the associated cl_node_id (currently on NavLA)

folder = 'Z:/VisionZero/GIS/Projects/LADOT_TrafficCounts/Manual Counts-20170526T005814Z-001/Manual Counts/'
filename = '1ST.HOPE.151112-NDSMAN.pdf'
path = folder + filename

#path = 'C:/Users/dotcid034/Downloads/temp/pdf_testing/Louise.SanJose.170328-NDSMAN.pdf'

def pdf_extract(path):

    # Load the PDF
    pdf = pdfquery.PDFQuery(path)
    pdf.load()

    # Create Empty Dict to organize the output
    Manual_TC = {}

    ##### Survey Information
    # Begin with reference points

    LabelList = ["North/South",'East/West','Day:','Date:','Weather:','Hours:','School Day:','District:','I/S CODE', 'WHEELED','BIKES','BUSES','AM PK 15 MIN', 'NORTHBOUND Approach', 'SOUTHBOUND Approach','EASTBOUND Approach','WESTBOUND Approach','XING S/L','XING N/L','XING W/L','XING E/L']
    
    Offsets = {}
    Offsets['North/South'] = [70,-5,350,15]
    Offsets['East/West'] = [70,-5,350,15]
    Offsets['Day:'] = [70,-5,120,15]
    Offsets['Date:'] = [30,-8,130,15]
    Offsets['Weather:'] = [30,-8,130,15]
    Offsets['Hours:'] = [30,-8,130,15]
    Offsets['School Day:'] = [40,-5,120,15]
    Offsets['District:'] = [40,-5,130,15]

    Label_coords = {}
    for label in LabelList:
        Label_coords[label] = {}
        Label_grab = pdf.pq('LTTextLineHorizontal:contains("%s")' % (label))
        Label_coords[label]['x0y0'] = {}
        print Label_grab.attr('x0')
        print Label_grab.attr('y0')
        Label_coords[label]['x0y0']['x0'] = float(Label_grab.attr('x0'))
        Label_coords[label]['x0y0']['y0'] = float(Label_grab.attr('y0'))

        try:
            Label_coords[label]['box_coords'] = [Offsets[label][0] + Label_coords[label]['x0y0']['x0'],
                                                 Offsets[label][1] + Label_coords[label]['x0y0']['y0'],
                                                 Offsets[label][2] + Label_coords[label]['x0y0']['x0'],
                                                 Offsets[label][3] + Label_coords[label]['x0y0']['y0']
                                                 ]
        except:
            pass

    print Label_coords

    NS_Label = pdf.pq('LTTextLineHorizontal:contains("North/South")')
    NS_left_coord = float(NS_Label.attr('x0'))
    NS_bottom_coord = float(NS_Label.attr('y0'))

    EW_Label = pdf.pq('LTTextLineHorizontal:contains("East/West")')
    EW_left_coord = float(EW_Label.attr('x0'))
    EW_bottom_coord = float(EW_Label.attr('y0'))

    Day_Label = pdf.pq('LTTextLineHorizontal:contains("Day:")')
    Day_left_coord = float(Day_Label.attr('x0'))
    Day_bottom_coord = float(Day_Label.attr('y0'))

    Date_Label = pdf.pq('LTTextLineHorizontal:contains("Date:")')
    Date_left_coord = float(Date_Label.attr('x0'))
    Date_bottom_coord = float(Date_Label.attr('y0'))

    Weather_Label = pdf.pq('LTTextLineHorizontal:contains("Weather:")')
    Weather_left_coord = float(Weather_Label.attr('x0'))
    Weather_bottom_coord = float(Weather_Label.attr('y0'))

    Hours_Label = pdf.pq('LTTextLineHorizontal:contains("Hours:")')
    Hours_left_coord = float(Hours_Label.attr('x0'))
    Hours_bottom_coord = float(Hours_Label.attr('y0'))

    School_Label = pdf.pq('LTTextLineHorizontal:contains("School Day:")')
    School_left_coord = float(School_Label.attr('x0'))
    School_bottom_coord = float(School_Label.attr('y0'))

    print Date_left_coord, Date_bottom_coord

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
        #('int_code', 'LTTextLineHorizontal:in_bbox("366,579,419,590")')
        ])

    # TESTING
    print survey_info
    exit()

    # Reformat date, add to Manual_TC
    print survey_info
    survey_info['date'] = datetime.strptime(survey_info['date'], '%B %d, %Y').date()
    Manual_TC['Info'] = survey_info

    ##### Special Vehicles: Dual-Wheeled, Bikes, Buses
    # Initial data grab
    special_veh_scrape = pdf.extract([
        ('with_formatter','text'),
        ('data', 'LTTextLineHorizontal:in_bbox("126,507,436,546")')
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
        ('NB', 'LTTextLineHorizontal:in_bbox("162,400,191,477")'),
        ('SB', 'LTTextLineHorizontal:in_bbox("244,400,271,477")'),
        ('EB', 'LTTextLineHorizontal:in_bbox("342,400,371,477")'),
        ('WB', 'LTTextLineHorizontal:in_bbox("424,400,453,477")')
        ])

    peak_vol_scrape = pdf.extract([
        ('with_formatter','text'),
        ('NB', 'LTTextLineHorizontal:in_bbox("125,400,162,477")'),
        ('SB', 'LTTextLineHorizontal:in_bbox("216,400,244,477")'),
        ('EB', 'LTTextLineHorizontal:in_bbox("315,400,342,477")'),
        ('WB', 'LTTextLineHorizontal:in_bbox("400,400,424,477")')
        ])

    peak_direction = []

    for direction in directions:
        
        peak_dict = {}    
        peak_time_split = peak_time_scrape[direction].split()
        peak_vol_split = peak_vol_scrape[direction].split()

        for i in range(0,4):
            peak_dict['type'] = peak_types[i]
            peak_dict['approach'] = direction
            peak_dict['time'] = peak_time_split[i]
            peak_dict['volume'] = peak_vol_split[i]
        peak_direction.append(peak_dict)

    # Append to Manual_TC
    Manual_TC['PeakVol'] = peak_direction

    ##### Survey Hours
    survey_hours = pdf.extract([
        ('with_formatter','text'),
        ('hours','LTTextLineHorizontal:in_bbox("46,290,76,349")')])

    survey_hours['hours'] = survey_hours['hours'].split()

    #Format survey hours using strptime
    for i in range(0, len(survey_hours['hours'])):
        hoursplit = survey_hours['hours'][i].split('-')
        starttime = time(int(hoursplit[0]))
        starttime = datetime.combine(survey_info['date'], starttime)
        endtime = time(int(hoursplit[1]))
        endtime = datetime.combine(survey_info['date'], endtime)
        survey_hours['hours'][i] = [starttime, endtime]

    ##### Volume Data
    # Initial data grab
    volume_scrape = pdf.extract([
        ('with_formatter','text'),
        ('NB', 'LTTextLineHorizontal:in_bbox("95,288,186,348")'),
        ('SB', 'LTTextLineHorizontal:in_bbox("280,288,366,349")'),
        ('EB', 'LTTextLineHorizontal:in_bbox("95,166,186,225")'),
        ('WB', 'LTTextLineHorizontal:in_bbox("280,166,366,224")')
        ])

    volume_extract = {}
    for direction in volume_scrape:
        volume_extract[direction] = {}
        volume_extract[direction]['Lt'] = volume_scrape[direction].split()[0:6]
        volume_extract[direction]['Th'] = volume_scrape[direction].split()[6:12]
        volume_extract[direction]['Rt'] = volume_scrape[direction].split()[12:18]

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
    ped_sch_scrape = pdf.extract([
        ('with_formatter','text'),
        ('SL', 'LTTextLineHorizontal:in_bbox("460,291,508,350")'),
        ('NL', 'LTTextLineHorizontal:in_bbox("515,292,567,350")'),
        ('WL', 'LTTextLineHorizontal:in_bbox("460,165,508,225")'),
        ('EL', 'LTTextLineHorizontal:in_bbox("515,165,567,225")')
        ])

    ped_sch_extract = {}
    for leg in ped_sch_scrape:
        ped_sch_extract[leg] = {}
        ped_sch_extract[leg]['Ped'] = ped_sch_scrape[leg].split()[0:6]
        ped_sch_extract[leg]['Sch'] = ped_sch_scrape[leg].split()[6:12]

    ped_sch_data = []
    for leg in ped_sch_extract:
        for pedtype in ped_sch_extract[leg]:
            for i in range(0,len(ped_sch_extract[leg][pedtype])):
                ped_sch_dict = {}
                ped_sch_dict['XingLeg'] = leg
                ped_sch_dict['Type'] = pedtype
                ped_sch_dict['start_time'] = survey_hours['hours'][i][0]
                ped_sch_dict['end_time'] = survey_hours['hours'][i][1]
                ped_sch_dict['volume'] = ped_sch_extract[leg][pedtype][i]
                ped_sch_data.append(ped_sch_dict)

    # Append to Manual_TC
    Manual_TC['Pedestrian'] = ped_sch_data

    ##### Return Final Dict
    print Manual_TC
    return Manual_TC


pdf_extract(path)


