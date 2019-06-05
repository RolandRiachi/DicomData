import numpy as np
from pydicom.filereader import dcmread
from os import symlink, makedirs
from os.path import join
import matplotlib.pyplot as plt

#Directories that will be written to
DCM_DIR = '/media/roland/WD_Passport/dcm_data' #Directory where symbolic links are stored
NPY_DIR = '/media/roland/WD_Passport/npy_data' #Directory where numpy arrays are stored

#File which contains all the filenames
FILENAMES = open('DCM_files.txt')

#File that error files will be written to
LOG = open('log.txt', 'w+')
TEST = open('test.txt', 'w+')

#Maximum dimensions of any DICOM file
X_MAX = 0 #4915
Y_MAX = 0 #6000

IMAGE_NUMBER = 0

#Each key is associated to an expert's 2 digit code
IDENTIFICATION_CODES = {'2219':'30', '9174':'10', '6756':'02',
                      '2237':'30', '9471':'10', '6815':'02',
                      '4074':'30', '9460':'10', '7139':'02',
                      '4348':'30', '9617':'10', '6859':'02',
                      '4394':'30', '9733':'10', '6804':'02',
                      '4689':'30', '10117':'10', '7028':'02',
                      '5262':'30', '10364':'10', '7047':'02',
                      '5323':'30', '10367':'10', '7095':'02',
                      '5420':'30', '10576':'10', '7133':'02',
                      '5586':'30', '10903':'10', '7402':'02',
                      '5703':'30', '11106':'10', '7589':'02',
                      '5776':'30', '11156':'10', '7636':'02',
                      '5929':'30', '11548':'10', '7865':'02',
                      '5934':'30', '11798':'10', '8371':'02',
                      '6161':'30', '12066':'10', '8534':'02',
                      '6326':'30', '12141':'10', '6599':'02',
                      '6486':'30', '12532':'10', '4076':'02',
                      '6571':'30', '12631':'10', '7360':'02',
                      '4713':'30', '12866':'10', '4817':'02',
                      '4964':'30', '12874':'10', '7530':'02',
                      '6504':'30', '8488':'10', '5960':'02',
                      '6528':'30', '9332':'10', '9467':'02',
                      '6868':'30', '9359':'10', '10924':'02',
                      '7245':'30', '10867':'10', '8536':'02',
                      '8038':'30', '10965':'10', '8658':'02'}

for file in FILENAMES.readlines():
    f = file.strip()

    #Try to open the image file
    try:
        dataset = dcmread(f, force=True)
        plt.imshow(dataset.pixel_array, cmap='gray')
        plt.close()
    except Exception as e:
        LOG.write(str(e) + ' | ' + f + '\n')
        continue

    #Build protocol name: LCC, RCC, LMLO, or RMLO
    try:
        #Left or Right view
        lat = dataset.ImageLaterality if hasattr(dataset, 'ImageLaterality') else dataset.Laterality

        #Name of the procedure
        p = dataset[0x0054, 0x0220].value[0].CodeMeaning.lower()
    #If no ImageLaterality, Laterality, or p -> then it's not a picture of a breast
    except AttributeError:
        continue

    IMAGE_NUMBER += 1

    #Build protocol: L + CC, R + CC, L + MLO, R + MLO, or other (would have to manually check these to see if they're good)
    if p == 'cranio-caudal':
        protocol = lat + 'CC'
    elif p == 'medio-lateral oblique' or p == 'latero-medial' or p == 'medio-lateral':
        protocol = lat + 'MLO'
    else:
        protocol = lat + p

    #Get names of directories in filepath
    directories = f.split('/')

    #Build each patient's unique identification code: 'expert code'-'key'-'patient number'
    identification = IDENTIFICATION_CODES[directories[5]] + '-' + directories[5] + '-' + directories[6]

    dims = dataset.pixel_array.shape

    #Update maximum dimensions if necessary
    X_MAX =  dims[1] if dims[1] > X_MAX else X_MAX
    Y_MAX = dims[0] if dims[0] > Y_MAX else Y_MAX

    print(join(DCM_DIR, identification, protocol + 'IMG' + '{:05}'.format(IMAGE_NUMBER) + '.dcm'))

    #Create soft link to file
#    try:
#        symlink(f, join(DCM_DIR, identification, protocol + 'IMG' + '{:05}'.format(IMAGE_NUMBER) + '.dcm'))
#    except FileNotFoundError:
#        makedirs(join(DCm_DIR, identification))
#        symlink(f, join(DCM_DIR, identification, protocol + 'IMG' + '{:05d}'.format(IMAGE_NUMBER) + '.dcm'))
#    except FileExistsError:
#        pass

    #Save pixel data as numpy array
#    try:
#        np.save(join(NPY_DIR, identification, protocol + 'IMG' + '{:05d}'.format(IMAGE_NUMBER) + '.npy'), np.flipud(pixel_data))
#    except FileNotFoundError:
#        makedirs(join(NPY_DIR, identification))
#        np.save(join(NPY_DIR, identification, protocol + 'IMG' + '{:05d}'.format(IMAGE_NUMBER) + '.npy'), np.flipud(pixel_data))
#    except FileExistsError:
#        pass

print('Max x dimension:', X_MAX)
print('Max y dimension:', Y_MAX)

FILENAMES.close()
LOG.close()
