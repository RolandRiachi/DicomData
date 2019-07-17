# DicomData

- **findDCM.sh** - Finds all DICOM files (excluding DICOMDIR files) in a directory and writes the absolute path to "DCM_files.txt"
- **create_hdf5.py** - Iterates over "DCM_files.txt" to find the last created file per protocol (right CC, left CC, right MLO, left MLO) per identification code, then writes each scan into an HDF5 file format called "DCM_data.hdf5".

## DCM_data.hdf5 File Structure

- Root (File)

  - Identification codes (Groups)

    - Patient info (Dataset):

      - Array of integer and float values that describe:
        - Age
        - Height (m)
        - Type of exam
        - Breast size
        - Breast type
        - Particular conditions
        - Beauty marks
        - Exams compared with previous exam
        - Right CC scan acceptable
        - Left CC scan acceptable
        - Right MLO scan acceptable
        - Left MLO scan acceptable
        - Overall CC acceptable
        - Overall MLO acceptable
        - Overall acceptable
        - Weight (Kg)
        - BMI
      - Attributes dictionary uses the dataset's array index as keys and the above labels as values

    - RIGHT_CC, LEFT_CC, RIGHT_MLO, LEFT_MLO (Dataset):

      - 3 dimensional pixel array of the mammogram, (sheet #, x, y).

    - RIGHT_CC_LABELS, LEFT_CC_LABELS (Dataset):

      - Array of integer values that describe:

        - Whether the image can be evaluated

        - Whether part of the image is cut-off
        - Whether the line from the nipple to the chest is perpendicular to the edge of the image
        - Whether there is good visualisation of deep tissue
        - Whether the line from the nipple to the chest on the CC is less than or equal to 1 cm from the line from the nipple to the pectoral on the MLO
        - Whether the nipple is seen from the side

        - Whether there are any artefacts or superposition
        - Whether the skin of the breast is folded

      - Attributes dictionary uses the dataset's array index as keys and the above labels as values

    - RIGHT_MLO_LABELS, LEFT_MLO_LABELS (Dataset):

      - Array of integer values that describe:

        - Whether the image can be evaluated
        - Whether part of the image is cut-off
        - Whether there is good visualisation of deep tissue
        - Whether there is adequate pectoral muscle in the image
        - Whether there is a maximal view of the pectoral muscle
        - Whether the nipple is seen from the side

        - Whether the infra-mammary angle is well open and shown
        - Whether there are any artefacts or superposition
        - Whether the skin of the breast is folded

      - Attributes dictionary uses the dataset's array index as keys and the above labels as values