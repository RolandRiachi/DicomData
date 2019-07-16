#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 14:43:41 2019

@author: roland
"""

from pydicom import read_file
import pandas as pd

#Open spreadsheet wtih image labels
data = pd.read_excel('/home/roland/Downloads/OTIMdataFINAL_corrected.xlsx')

#Get dates associated to identification codes in spreadsheet
dates = dict()
for r in data.index:
    #Get identification code from spreadsheet
    #Remove first 3 chars from code, 'XX-', because it's bothersome to figure this out from the DICOM filename
    iden = data.iloc[r, 3][3:]
    
    d = str(data.iloc[r, 4].date()).split('-')
    
    #No information regarding time
    if d[0] == 'NaT':
        continue
    
    #Rewrite to same format as DICOM file dates
    date = d[0] + d[1] + d[2]
    
    dates[iden] = date

#Ignore are files that can't be read by SimpleITK and pydicom, 
#Files in 'DCM_files.txt' and 'out_2.txt' appear in the same relative order, use readline() to save a bit on performance
with open('DCM_files.txt') as src, open('ignore_files.txt') as ignore, open('times_2.txt', 'w+') as out:
    ign = ignore.readline().strip()
    
    for f in src:
        fname = f.strip()
        
        #Verbose
        print(fname)
        
        #Skip unopenable files and get next filename to ignore
        if fname == ign:
            ign = ignore.readline().strip()
            continue
        
        #Build identification code from filename
        path = fname.split('/')
        
        #Ignore files from this specific directory
        if path[6] == '10_ancien':
            continue
        
        #Handle wierd directory names, e.g.: 'PATIENTE 1' or '01-lastname,firstname'
        if path[6][:2].isdigit():
            iden = path[5] + '-' + path[6][:2]
        elif path[6][-2:].isdigit():
            iden = path[5] + '-' + path[6][-2:]
        else:
            iden = path[5] + '-0' + path[6][-1]
        
        #Write filename to output if date in DICOM file matches date from data
        try:
            ds = read_file(fname)
            
            data_date = dates[iden]
            file_date = ds.AcquisitionDate
            if hasattr(ds, 'AcquisitionDate'):
                file_date = ds.AcquisitionDate
            elif hasattr(ds, 'ContentDate'):
                file_date = ds.ContentDate
            else:
                file_date = ds.SeriesDate
            
            p = ds[0x0008, 0x0068].value
        except AttributeError:
            continue
        except KeyError:
            continue

        
        if file_date == data_date and p == 'FOR PRESENTATION':
            out.write(f)




