from pydicom import dcmread
import matplotlib.pyplot as plt
from os import listdir, chdir

#Open one file or open directory
READFILE = True

FILE = ''
DIR = ''

if READFILE:
    ds = dcmread(FILE)
    plt.imshow(ds.pixel_array, cmap='gray')
    plt.show()
else:
    chdir(DIR)
    for f in listdir(DIR):
#        print(f)
        ds = dcmread(f)
        plt.imshow(ds.pixel_array, cmap='gray')
        plt.show()
