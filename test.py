from pydicom import read_file
import SimpleITK as sitk
import matplotlib.pyplot as plt

FILE = open('good_files.txt')

reader = sitk.ImageFileReader()
reader.LoadPrivateTagsOn()

for f in FILE.readlines()[11573:11597]:
    ds = read_file(f.strip())
    try:
        print(f.strip())
#        print(ds.values)
        print(ds[0x0008, 0x0020].value, ds[0x0008, 0x0021].value, ds[0x0008, 0x0022].value)
        print(ds[0x0008, 0x0068].value)
        
        print('---------------------------------------------------------------------------------------')
    
        reader.SetFileName(f.strip())
        reader.ReadImageInformation()
    
    #    try:
    #        print(reader.GetMetaData('0054|0220'))
    #    except:
    #        print(f.strip())
        
        image = reader.Execute()
        
        plt.imshow(sitk.GetArrayFromImage(image)[0], cmap='gray')
        plt.show()
    except KeyError:
        pass
    except RuntimeError:
        pass
    #/media/roland/WD_Passport/Anonymes/10367/01/BOUCHARD,JOCELYNE 2013/00000001
    #/media/roland/WD_Passport/Anonymes/10367/07/simard,chantale 2017/00000001
#    print(ds.values)
#    print(ds[0x0008, 0x0068].value)
#    print(ds.ProtocolName)
