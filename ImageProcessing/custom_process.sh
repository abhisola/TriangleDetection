#!/bin/bash
# racks to process
RACKS=('000102')
DATE=$1
if [ -z $DATE ]
  then
    DATE=$(date +%Y-%m-%d -d "yesterday")
fi
# optionally input an end date, will run up to that date but NOT including that date
ENDDATE=$2

# if no enddate specified
if [ -z $ENDDATE ] 
then
  #echo "Processing $DATE  "
  for i in "${RACKS[@]}"
  do
    python processrackimages.py -r $i -d $DATE
  done
# otherwise run up to the end date, NOT including the end date
else
  while [ "$DATE" != $ENDDATE ]; do 
    echo "Processing $DATE  "
    for i in "${RACKS[@]}"
    do
      python processrackimages.py -r $i -d $DATE
    done
    DATE=$(date -I -d "$DATE + 1 day")
  done
fi

