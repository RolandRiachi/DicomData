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
    
    def get_full_iden(self, iden):
        ''''''
        return self.sheet.iloc[self.rows[iden], 3]

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

if __name__ == '__main__':
    #Set constants
    ATTRS = Attributes('/home/roland/Downloads/OTIMdataFINAL_corrected.xlsx')    
    #Which codes to ignore - these patients currently have more than 4 scans associated with them in corrected_correct_times
#    IGNORE = ['10867-08', '10867-10', '10867-12', '10903-10', '11106-07', '11106-11', '11156-14', '12141-13', '12141-14', '12874-07', '12874-09', '12874-11', '12874-13', '12874-15', '2219-06', '2237-04', '4964-03', '4964-07', '4964-09', '5262-02', '5323-04', '5703-06', '5703-10', '5776-14', '5960-13', '6504-02', '6815-05', '6815-08', '6868-04', '7047-02', '7047-03', '7047-12', '7047-15', '7245-15', '7530-02', '7530-05', '7530-15', '7589-03', '7636-13', '7636-14', '8851-12', '8851-13', '8851-14', '9174-09', '9174-13', '9332-04', '9332-06', '9332-08', '9332-11', '9332-14', '9332-15', '9467-05', '9733-13']
    
    #Set up SimpleITK
    reader = sitk.ImageFileReader()
    reader.LoadPrivateTagsOn()
    
    with open('times.txt') as FILE, h5py.File('DCM_data_5.hdf5', 'a') as OUT:
#        for f in FILE.readlines()[:3695]:
        for f in FILE:
            fname = f.strip()
            
            #Verbose
            print(fname)
            
            #Get full identification code of patient
            path = fname.split('/')
#            iden = path[5] + '-' + path[6][:2]
            
            if path[6][:2].isdigit():
                iden = path[5] + '-' + path[6][:2]
            elif path[6][-2:].isdigit():
                iden = path[5] + '-' + path[6][-2:]
            else:
                iden = path[5] + '-0' + path[6][-1]
            
#            if iden in IGNORE:
#            if iden not in IGNORE:
            full_iden = ATTRS.get_full_iden(iden)
            
            #Create group if missing, empty dataset that stores patient info as attributes and get scan attributes
            if full_iden not in OUT:
                RIGHT_CC_time, LEFT_CC_time, RIGHT_MLO_time, LEFT_MLO_time = 0, 0, 0, 0
                grp = OUT.require_group(full_iden)
                
                #Set patient info attributes
                patient_dict = ATTRS.read_patient_info(iden)
                patient_info = grp.create_dataset('patient_info', data=list(patient_dict.values()), compression='gzip')
                Attributes.set_dataset_attrs(patient_info, list(patient_dict.keys()))
                
                RIGHT_CC_dict, LEFT_CC_dict, RIGHT_MLO_dict, LEFT_MLO_dict = ATTRS.read_scan_info(iden)
            
            #Check scan protocol
            dataset = read_file(fname)
            lat = dataset.ImageLaterality if hasattr(dataset, 'ImageLaterality') else dataset.Laterality
            p = dataset[0x0054, 0x0220].value[0].CodeMeaning.lower()
            
            #Build protocol: L + CC, R + CC, L + MLO, R + MLO, or other (would have to manually check these to see if they're good)
            if p == 'cranio-caudal':
                protocol = lat + 'CC'
            elif p == 'medio-lateral oblique' or p == 'latero-medial' or p == 'medio-lateral':
                protocol = lat + 'MLO'
            elif 'exaggerated' in p:
                continue
            else:
                raise KeyError('Naming protocol went wrong at ' + fname)
                
            scan_time = float(dataset.AcquisitionTime)
            
            #Load data from file
            reader.SetFileName(fname)
            image = reader.Execute()
    
            #Write scan to file 
            if protocol == 'RCC' and scan_time > RIGHT_CC_time:
#                if protocol == 'RCC':
                #Create first scan or delete and replace old one
                if RIGHT_CC_time == 0:
                    grp.create_dataset('RIGHT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')
                    RIGHT_CC_LABELS = grp.create_dataset('RIGHT_CC_LABELS', data=list(RIGHT_CC_dict.values()), compression='gzip')
                    Attributes.set_dataset_attrs(RIGHT_CC_LABELS, list(RIGHT_CC_dict.keys()))
                else:
                    del grp['RIGHT_CC']
                    grp.create_dataset('RIGHT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')
                
                RIGHT_CC_time = scan_time
            elif protocol == 'LCC' and scan_time > LEFT_CC_time:
#                elif protocol == 'LCC':
                #Create first scan or delete and replace old one
                if LEFT_CC_time == 0:
                    grp.create_dataset('LEFT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')
                    LEFT_CC_LABELS = grp.create_dataset('LEFT_CC_LABELS', data=list(LEFT_CC_dict.values()), compression='gzip')
                    Attributes.set_dataset_attrs(LEFT_CC_LABELS, list(LEFT_CC_dict.keys()))
                else:
                    del grp['LEFT_CC']
                    grp.create_dataset('LEFT_CC', data=sitk.GetArrayFromImage(image), compression='gzip')

                LEFT_CC_time = scan_time
            elif protocol == 'RMLO' and scan_time > RIGHT_MLO_time:
#                elif protocol == 'RMLO':
                #Create first scan or delete and replace old one
                if RIGHT_MLO_time == 0:
                    grp.create_dataset('RIGHT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')
                    RIGHT_MLO_LABELS = grp.create_dataset('RIGHT_MLO_LABELS', data=list(RIGHT_MLO_dict.values()), compression='gzip')
                    Attributes.set_dataset_attrs(RIGHT_MLO_LABELS, list(RIGHT_MLO_dict.keys()))
                else:
                    del grp['RIGHT_MLO']
                    grp.create_dataset('RIGHT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')

                RIGHT_MLO_time = scan_time
            elif protocol == 'LMLO' and scan_time > LEFT_MLO_time:
#                else:
                #Create first scan or delete and replace old one
                if LEFT_MLO_time == 0:
                    grp.create_dataset('LEFT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')
                    LEFT_MLO_LABELS = grp.create_dataset('LEFT_MLO_LABELS', data=list(LEFT_MLO_dict.values()), compression='gzip')
                    Attributes.set_dataset_attrs(LEFT_MLO_LABELS, list(LEFT_MLO_dict.keys()))
                else:
                    del grp['LEFT_MLO']
                    grp.create_dataset('LEFT_MLO', data=sitk.GetArrayFromImage(image), compression='gzip')

                LEFT_MLO_time = scan_time
                       
            
#/media/roland/WD_Passport/Anonymes/10367/07/simard,chantale 2017/00000001

#Go through correct_times [:298]
#Get full iden <- get_full_iden
#Make a group named after full iden if it doesn't exist <- require_group, read_scan_info at group_creation and break array up
#create empty [] with read_patient_info as attribute <- contains then require_dataset
#Check if file is RCC,LCC,RMLO,LMLO - create dataset and attach attrs <- contains then require_dataset