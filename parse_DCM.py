#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 11:01:50 2019

@author: roland
"""

import SimpleITK as sitk
from pydicom import read_file
import pandas as pd

FILES = open('good_files.txt')
OUT = open('correct_times.txt', 'a')
DATA = pd.read_excel('/home/roland/Downloads/OTIMdataFINAL.XLSX')
TIMES = [(DATA.iloc[r, 3][3:], DATA.iloc[r, 4]) for r in DATA.index]

TIMES = []
for r in DATA.index:
    iden = DATA.iloc[r, 3][3:]
    t = str(DATA.iloc[r, 4].date()).split('-')
    
    if t[0] == 'NaT':
        continue
    
    time = t[0] + t[1] + t[2]
    TIMES.append((iden, time))
    
TIMES = dict(TIMES)

reader = sitk.ImageFileReader()
reader.LoadPrivateTagsOn()

for f in FILES.readlines()[2577:]: #1639
    print(f.strip())
    path = f.split('/')
    iden = path[5] + '-' + path[6]
    
    try:
        data_time = TIMES[iden]
        
        ds = read_file(f.strip())
        reader.SetFileName(f.strip())
        reader.ReadImageInformation()
        
#        file_time = reader.GetMetaData('0008|0022')
        file_time = ds[0x0008, 0x0022].value
        p = ds[0x0008, 0x0068].value
#        p = ds[0x0054, 0x0220].value[0].CodeMeaning
    except RuntimeError:
        continue
    except KeyError:
        continue
    
    if file_time == data_time and p == 'FOR PRESENTATION':
        OUT.write(f)
        
#Look for files of only RCC,LCC,RMLO,LMLO
#Have to get rid of routine images
        #0008, 103e == L CC, ... or if length of desc > 8 or smth?

#Might be an error in spreadsheet 10576-12 date column? It says 14-05-2017 but its actually 14-06-2017?
             
#/media/roland/WD_Passport/Anonymes/10576/12/SynapseMediaSets 656681/Syn20170703121355/DICOMOBJ/00000001
#/media/roland/WD_Passport/Anonymes/10576/12/SynapseMediaSets 656681/Syn20170703121355/DICOMOBJ/00000002
#/media/roland/WD_Passport/Anonymes/10576/12/SynapseMediaSets 656681/Syn20170703121355/DICOMOBJ/00000005
#/media/roland/WD_Passport/Anonymes/10576/12/SynapseMediaSets 656681/Syn20170703121355/DICOMOBJ/00000006

#Error in 10903-10 date column? It says 12-06-2017 but its actually 10-06-2017?

#/media/roland/WD_Passport/Anonymes/10903/10/DICOMOBJ/00000001
#/media/roland/WD_Passport/Anonymes/10903/10/DICOMOBJ/00000002
#/media/roland/WD_Passport/Anonymes/10903/10/DICOMOBJ/00000003
#/media/roland/WD_Passport/Anonymes/10903/10/DICOMOBJ/00000004
        
#What to do for 12141???

#Error in 2219-12 date column? It says 22-08-2017 but its actually 22-03-2017
#4394-03? it says 2017-03-24 but its actually 2017-05-15
#4094-10 should actually be 4394-10?
#4689-09? it says 2017-03-09 but its actually 2017-03-16
#4817-06 to 4817-08? 4817-10? it says 2017-07-03 but its actually 2017-07-04
#4817-09 to 4817-10? it says 2017-07-3 but its actually 2017-07-07
#4969-02 should actually be 4964-02?
#5262-09? it says 2017-06-09 but its actually 2017-06-08
#5420-13? it says 2017-03-19 but its actually 2017-03-18
#5420-14? it says 2017-03-19 but its actually 2017-03-18
#5589-09 should actually be 5586-09
#5703-09? it says 2017-06-06 but its actually 2017-06-09
#5776-06? it says 2017-05-05 but its actually 2017-05-25
#5960-01? it says 2017-07-07 but its actually 2017-07-11
#6326-07? it says 2017-10-05 but its actually 2017-05-10
#6356-12 should actually be 6326-12
#6326-14? it says 2017-10-12 but its actually 2017-05-12
#6405-05 should actually be 6504-05
#6504-11? it says 2017-10-22 but its actually 2017-06-22
#6405-14 should actually be 6504-14
#6756-05 time
#6756-06 time
#5756-09 should be 6756-09
#6804-11 time
#6815-02 time
#7047-08 time
#7530-01 too many files
#7530-03 time
#7530-04 time
#7865-01 time
#7865-14 time
#8534-06 time
#8534-12 to 8534-15 time
#8536-09 time
#8558-05 should be 8658-05
#8851-04 time
#5581-05 should be 8851-05
#8851-06, 8851-07 time
#9406-04 should be 9460-04
#9467-06 to 9467-09 time
#9617-01 time
#


























        











