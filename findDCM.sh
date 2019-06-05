#!/bin/bash

SAVEIFS=$IFS
IFS=$'\n'

SRC="/media/roland/WD_Passport/Anonymes/"
TYPE=": DICOM medical imaging data"
OUT="DCM_files.txt"
FILES=$(find $SRC)

for f in $FILES
do
	#If DICOM file and not a DICOMDIR file
	if [[ "$(file "$f" -0 | cut -d '' -f2)" == "$TYPE" && ! "$f" == *"DICOMDIR" ]]
	then
		echo "$f" >> $OUT
	fi
done

IFS=$SAVEIFS
