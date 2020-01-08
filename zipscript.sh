#!/bin/sh

check_content() {
	FOUND=0
	for FILE in *
	do
		if [ ${FILE: -3} == ".py" ] || [ "$FILE" = "index.js" ]
		then
	  		FOUND=1
	  		break
	  	fi
	done
	echo "$FOUND"
}

make_zip() {
	eval "rm -rf $1.zip"
	ZIP_CALL="zip -r $1"
	for FILE in *
	do
	  	ZIP_CALL="$ZIP_CALL $FILE"
	done
	eval $ZIP_CALL
}

scan_directory() {
	if [ -d "$1" ]
	then
		eval "cd $1"
		DIR="${PWD##*/}"
		FOUND=$(check_content $DIR)
		if [ $FOUND = 1 ]
		then
			make_zip $DIR
		else
			for FILE in *
			do
				scan_directory $FILE
			done
		fi
		cd ..
	fi
}

BASEDIR=$(dirname "$0")

for SUBDIR in $BASEDIR/*
do
	scan_directory $SUBDIR
done

exit 1
