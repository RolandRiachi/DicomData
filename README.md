# DicomData

- **findDCM.sh** - Finds all DICOM files (excluding DICOMDIR files) in a directory and writes the absolute path to "DCM_files.txt"

- **process_files.py** - Creates soft links to files in "DCM_files.txt" and saves pixel data of medical images in a hierarchy by patient identification code. Ex: `some_parent/dcm_data/10-10364-01/LCCIMG12345.dcm` and `some_parent/npy_data/10-10364-01/LCCIMG12345.npy`.
- **openDCM.py** - Either opens the medical image of a single DICOM file or opens tries to open the medical image of all DICOM files in a directory, depending on a flag.

## On Opening DICOM Files

When opening some of the DICOM files using pydicom, python raises an `NotImplementedError` for the `get_pixeldata` method. Below is a fix that was ran in a virtualenv:

```Bash
. bin/activate
pip3.6 install numpy pydicom
sudo git clone --branch master https://github.com/HealthplusAI/python3-gdcm.git && cd python3-gdcm && sudo dpkg -i build_1-1_amd64.deb && sudo apt-get install -f	
cd ../
cp /usr/local/lib/gdcm.py ./lib/python3.6/site-packages/
cp /usr/local/lib/gdcmswig.py ./lib/python3.6/site-packages/
cp /usr/local/lib/_gdcmswig.so ./lib/python3.6/site-packages/
cp /usr/local/lib/libgdcm* ./lib/python3.6/site-packages/
sudo ldconfig
```