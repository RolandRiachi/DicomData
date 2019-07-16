import h5py
import pandas as pd
import numpy as np

class Attributes:
    '''
    Patient identification code is already known - will be passed here
    Excel spreadsheet is already loaded
    '''

    def __init__(self, xlsx):
        self.sheet = pd.read_excel(xlsx) #Spreadsheet of all patients' information
        self.rows = dict([(ind[3:], col) for col, ind in self.sheet.iloc[:, 3].items()]) #Dict with key = patient identification code, value = spreadsheet row #

        #age, height (m), weight (kg), bmi, type of examination, breast size/shape, conditions, beauty marks, compared with prior images
        self.patient_info_cols = [6, 9, 12, 13, 14, 15, 16, 17, 75, 76, 77, 78, 79, 80, 81, 82, 83]
        
        #RCC, LCC, RMLO, LMLO
        self.img_cols = [[i for i in range(18, 33, 2)], [i for i in range(19, 34, 2)], [i for i in range(34, 52, 2)], [i for i in range(35, 53, 2)]]

    def read_patient_info(self, iden):
        return dict(self.sheet.iloc[self.rows[iden], self.patient_info_cols])

    def read_scan_info(self, iden):
        return [dict(self.sheet.iloc[self.rows[iden], c]) for c in self.img_cols]
    
    def get_full_iden(self, iden):
        return self.sheet.iloc[a.rows[iden], 3]


if __name__ == '__main__':
    a = Attributes('/home/roland/Downloads/OTIMdataFINAL.XLSX')
    
#    print(a.get_full_iden('6528-13'))
#    
#    x = a.read_scan_info('6528-13')
#    y = [True, False, False, False]
#    z = [x[i] if y[i] else None for i in range(4)]
    
    f = h5py.File('foo.h5py', 'a')
    grp = f.require_group('30-6528-13')
    ds = grp.require_dataset('test', (), dtype='f')
    for k, v in a.read_patient_info('6528-13').items():
        ds.attrs[k] = v
    for x in ds.attrs.values():
        if type(x) == str:
            print(int(x[0]))
        else:
            print(x)
            
    #Go through 'good' files - build 
