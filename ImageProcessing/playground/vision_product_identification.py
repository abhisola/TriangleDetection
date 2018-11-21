import boto3
import botocore
import subprocess
import os, shutil, sys
import time
from os import path
from datetime import date, timedelta
import psycopg2
import json
with open('../settings.json') as jsonData:
  settings = json.load(jsonData)
  jsonData.close()
hostname = settings['postgres']['hostname']
username = settings['postgres']['username']
password = settings['postgres']['password']
database = settings['postgres']['database']
aws = settings['s3']['url']
bucket_name = settings['s3']['bucket']

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cursor = conn.cursor()

def main(argv):
    # set default date to yesterday
    yesterday = date.today() - timedelta(1)
    subjectDate = yesterday.strftime('%Y-%m-%d')
    dateParts = subjectDate.split("-")
    subjectYear = dateParts[0]
    subjectMonth = dateParts[1]
    subjectDay = dateParts[2]
    date_recorded = subjectYear + "-" + subjectMonth + "-" + subjectDay
    select_data = "SELECT * FROM shelf_stock "
    + "WHERE date_recorded > '" + date_recorded + "0800" + "' AND date_recorded < '" + date_recorded + "2200" + "'"
    + "AND racknum = '" + "000004" + "' "
    + "AND shelf_num = '" + "0" + "' "
    + "ORDER BY shelf_stock.date_recorded DESC LIMIT 1"
    print(select_data)


    getData(select_data)



def getData() :
    pass

def usage():
    print("python vision.py -r 000000 -d YYYY-MM-DD")
    print("  -r 000000 : unique rack ID number")
    print("  -d YYYY-MM-DD : UTC date ex: 2016-11-28")

# call main function
if __name__ == "__main__":
    main(sys.argv[1:])
