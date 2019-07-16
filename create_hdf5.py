#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 13:46:29 2019

@author: roland
"""

import h5py
import pandas as pd
import SimpleITK as sitk
import numpy as np
from pydicom import read_file

class Attributes:
    def __init__(self, xlsx):
        self.sheet = pd.read_excel(xlsx) #Spreadsheet of all patients' information
        self.rows = dict([(ind[3:], col) for col, ind in self.sheet.iloc[:, 3].items()]) #Dict with key = patient identification code, value = spreadsheet row #

        #age, height (m), weight (kg), bmi, type of examination, breast size/shape, conditions, beauty marks, compared with prior images, scan labels
        self.patient_info_cols = [6, 9, 12, 13, 14, 15, 16, 17, 75, 76, 77, 78, 79, 80, 81, 82, 83]
        
        #RCC, LCC, RMLO, LMLO
        self.img_cols = [[i for i in range(18, 33, 2)] + [75], [i for i in range(19, 34, 2)] + [76], [i for i in range(34, 52, 2)] + [77], [i for i in range(35, 53, 2)] + [78]]

    def read_patient_info(self, iden):
        return Attributes.to_int(dict(self.sheet.iloc[self.rows[iden], self.patient_info_cols]))

    def read_scan_info(self, iden):
        return [Attributes.to_int(dict(self.sheet.iloc[self.rows[iden], c])) for c in self.img_cols]
    
    def get_full_code(self, iden):
        return self.sheet.iloc[self.rows[iden], 3]

    def write_to_out(self, o, c, d):
        full_code = self.get_full_code(c)
        
        grp = out.require_group(full_code)
            
        #Set patient info attributes
        patient_dict = self.read_patient_info(c)
        patient_info = grp.create_dataset('patient_info', data=list(patient_dict.values()), compression='gzip')
        Attributes.set_dataset_attrs(patient_info, list(patient_dict.keys()))
        
        RIGHT_CC_dict, LEFT_CC_dict, RIGHT_MLO_dict, LEFT_MLO_dict = self.read_scan_info(c)
        
        for p in d.keys():
            #Load data from file
            reader.SetFileName(d[p][0])
            image = reader.Execute()
            
            #Write scan to file 
            if p == 'RCC':
                grp.create_dataset('RIGHT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')
                RIGHT_CC_LABELS = grp.create_dataset('RIGHT_CC_LABELS', data=list(RIGHT_CC_dict.values()), compression='gzip')
                Attributes.set_dataset_attrs(RIGHT_CC_LABELS, list(RIGHT_CC_dict.keys()))
            elif p == 'LCC':
                grp.create_dataset('LEFT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')
                LEFT_CC_LABELS = grp.create_dataset('LEFT_CC_LABELS', data=list(LEFT_CC_dict.values()), compression='gzip')
                Attributes.set_dataset_attrs(LEFT_CC_LABELS, list(LEFT_CC_dict.keys()))
            elif p == 'RMLO':
                grp.create_dataset('RIGHT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')
                RIGHT_MLO_LABELS = grp.create_dataset('RIGHT_MLO_LABELS', data=list(RIGHT_MLO_dict.values()), compression='gzip')
                Attributes.set_dataset_attrs(RIGHT_MLO_LABELS, list(RIGHT_MLO_dict.keys()))
            elif p == 'LMLO':
                grp.create_dataset('LEFT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')
                LEFT_MLO_LABELS = grp.create_dataset('LEFT_MLO_LABELS', data=list(LEFT_MLO_dict.values()), compression='gzip')
                Attributes.set_dataset_attrs(LEFT_MLO_LABELS, list(LEFT_MLO_dict.keys()))
                
    @staticmethod
    def set_dataset_attrs(ds, a):
        for i in range(len(a)):
            ds.attrs[str(i)] = a[i]
            
    @staticmethod    
    def to_int(dictionary):
        '''Replaces string values in a dictionary with integer first character of string'''
        for k, v in  dictionary.items():
            if type(v) == str:
                dictionary[k] = int(v[0])
            elif not np.isnan(v) and v == int(v):
                dictionary[k] = int(v)
            else:
                dictionary[k] = v
        
        return dictionary

def get_partial_code(fname):
    path = fname.split('/')
    
    if path[6][:2].isdigit():
        return path[5] + '-' + path[6][:2]
    elif path[6][-2:].isdigit():
        return path[5] + '-' + path[6][-2:]
    else:
        return path[5] + '-0' + path[6][-1]

def get_protocol_name(ds):
    l = dataset.ImageLaterality if hasattr(dataset, 'ImageLaterality') else dataset.Laterality
    p = dataset[0x0054, 0x0220].value[0].CodeMeaning.lower()
        
    #Build protocol: L + CC, R + CC, L + MLO, R + MLO, or other (would have to manually check these to see if they're good)
    if p == 'cranio-caudal':
        return l + 'CC'
    elif p == 'medio-lateral oblique' or p == 'latero-medial' or p == 'medio-lateral':
        return l + 'MLO'
    else:
        raise AttributeError
        
def get_scan_datetime(ds):
    if hasattr(ds, 'AcquisitionDate') and hasattr(ds, 'AcquisitionTime'):
        return float(ds.AcquisitionDate), float(ds.AcquisitionTime)
    elif hasattr(ds, 'ContentDate') and hasattr(ds, 'ContentTime'):
        return float(ds.ContentDate), float(ds.ContentTime)
    else:
        return float(ds.SeriesDate), float(ds.SeriesTime)

if __name__ == '__main__':
    #Set constants
    attrs = Attributes('/home/roland/Downloads/OTIMdataFINAL_corrected.xlsx')    
    #Which codes to ignore - these patients currently have more than 4 scans associated with them in corrected_correct_times
    ign = ['4394-09', '6815-0M', '10903-06', '6504-12', '7636-12', '10364-02', '11798-02']
    good_scans = {}
    curr_code = None
    
    reader = sitk.ImageFileReader()
    with open('DCM_files.txt') as src, h5py.File('DCM_data_3.hdf5', 'a') as out:
#        for f in FILE.readlines()[:3695]:
        for f in src:
            filename = f.strip()
            
            partial_code = get_partial_code(filename)
        
            if partial_code in ign:
                continue

            #Get relevant information
            dataset = read_file(filename)
            try:
                protocol = get_protocol_name(dataset)
                scan_date, scan_time = get_scan_datetime(dataset)
            except AttributeError:
                continue
                
            if partial_code == curr_code:
                if protocol in good_scans[curr_code]:
                    if scan_date > good_scans[curr_code][protocol][1]:
                        good_scans[curr_code][protocol] = (filename, scan_date, scan_time)
                    elif scan_date ==  good_scans[curr_code][protocol][1]:
                        if scan_time > good_scans[curr_code][protocol][2]:
                            good_scans[curr_code][protocol] = (filename, scan_date, scan_time)
                        else:
                            pass
                    else:
                        pass
                else:
                    good_scans[curr_code][protocol] = (filename, scan_date, scan_time)
            else:              
                if curr_code:
                    print(curr_code)
                    attrs.write_to_out(out, curr_code, good_scans[curr_code])                        
                
                good_scans[partial_code] = {}
                good_scans[partial_code][protocol] = (filename, scan_date, scan_time)
                curr_code = partial_code

            
            