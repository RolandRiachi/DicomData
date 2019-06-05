from pydicom import dcmread
from os import walk
from os.path import join

DCM_DIR = '/media/roland/WD_Passport/dcm_data'
NPY_DIR = '/media/roland/WD_Passport/npy_data'

for root, subdirs, files in walk(DCM_DIR):
    for file in files:
        #ImageLaterality/Laterality is in every file
        #ds[0x0054, 0x0220].value[0].CodeMeaning in every file
        #If not there, probably not a picture of a breast
        #cranio-caudel, medio-lateral oblique in almost all files - have to .lower first
        #latero-medial in some, some have 'exagerated'
        ds = dcmread(join(root, file))

        try:
#            protocol = ds.ProtocolName

#            protocol = ds[0x0055, 0x1001].value[0] + ds[0x0055, 0x1001].value[2:]
#            protocol = ds.ImageLaterality + ds.ViewPosition
#            protocol = ds[0x0018, 0x1400].value
#            protocol = ds[0x0045, 0x101b].value
#            protocol = ds[0x0008, 0x0104].value
#            laterality = 'L' if ds.SeriesDescription[0] == 'G' else 'R'
#            protocol = laterality + ds.SeriesDescription[2:]
#            protocol = ds[0x0054, 0x0220].value[0].CodeMeaning
#            print(protocol)

            lat = ds.ImageLaterality if hasattr(ds, 'ImageLaterality') else ds.Laterality

            protocol = ds[0x0054, 0x0220].value[0].CodeMeaning.lower()
            if protocol == 'cranio-caudal':
                p = 'CC'
            elif protocol == 'medio-lateral oblique' or protocol == 'latero-medial' or protocol == 'medio-lateral':
                p = 'MLO'
            else:
                p = protocol

            print(lat + p)
        except:
            print(join(root,file))
