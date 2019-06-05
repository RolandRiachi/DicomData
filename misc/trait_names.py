from pydicom import dcmread
import matplotlib.pyplot as plt

file = '/media/roland/WD_Passport/Anonymes/4074/01/DICOM/PA000001/ST000001/SE000003/IM000001'
ds = dcmread(file)

plt.imshow(ds.pixel_array, cmap='gray')
#plt.show()
print(ds.trait_names)
print(ds[0x0054, 0x0220].value[0].CodeMeaning)
