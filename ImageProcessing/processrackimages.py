import sys
import getopt
import json
import subprocess
import os
import psycopg2
from datetime import date, timedelta


with open('settings.json') as jsonData:
  settings = json.load(jsonData)
  jsonData.close()

hostname = settings['postgres']['hostname']
username = settings['postgres']['username']
password = settings['postgres']['password']
database = settings['postgres']['database']
aws = settings['s3']['url']

# main program entry point - decode parameters, act accordingly
def main(argv):
  # set default date to yesterday
  yesterday = date.today() - timedelta(1)
  subjectDate = yesterday.strftime('%Y-%m-%d')
  dateParts = subjectDate.split("-")
  subjectYear = dateParts[0]
  subjectMonth = dateParts[1]
  subjectDay = dateParts[2]

  # parse commandline parameters
  try:
    opts, args = getopt.getopt(argv, "r:d:")
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  if opts is None:
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-r':
      rackNum = arg
    elif opt == '-d':
      subjectDate = arg
      dateParts = subjectDate.split("-")
      subjectYear = dateParts[0]
      subjectMonth = dateParts[1]
      subjectDay = dateParts[2]
      if len(dateParts) != 3 or len(subjectYear) != 4 or len(subjectMonth) != 2 or len(subjectDay) != 2 :
        print("Invalid date")
        usage()
        sys.exit(2)

  if rackNum == '' or subjectDate == '':
    usage()
    sys.exit(2)

  # load rack details
  with open( 'rackDetails.json' ) as jsonData:
    rackDetails = json.load( jsonData )
    jsonData.close()

  # grab images from S3
  path = rackNum + "/" + subjectYear + "/" + subjectMonth + "/" + subjectDay
  sys.stdout.write(path + " ")
  command = "aws s3 sync s3://"+settings['s3']['bucket']+"/" + path + " /tmp/s3/" + path
  try:
      process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
      process.wait(60)
  except subprocess.TimeoutExpired:
    pass

  # setup DB
  conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
  cursor = conn.cursor()

  # process each image
  sys.stdout.flush()
  triangles = list()
  last_value = dict()
  for filename in sorted(os.listdir('/tmp/s3/' + path)):
    filenameParts = filename.split("-")
    shelf_num = filenameParts[0]
    # date_recorded = subjectYear + "-" + subjectMonth + "-" + subjectDay + " " + filenameParts[1][:-4]
    date_recorded = subjectYear + "-" + subjectMonth + "-" + subjectDay + " " + filenameParts[1]
    dateString = date_recorded[0:-4]
    command = '''python shelfspace.py {0} -i "/tmp/s3/{1}/{2}" '''.format(rackDetails[rackNum][filenameParts[0]]["args"],path,filename)
    print('\n'+filename)

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait(1)
    except subprocess.TimeoutExpired:
      pass
    
    detectionDetails = json.load( process.stdout )

    # lookup last value if we don't already have one

    if shelf_num not in last_value:
      cursor.execute(
        "SELECT percent_full FROM shelf_stock "
         + "WHERE date_recorded < '" + dateString + "'"
         + "AND racknum = '" + rackNum + "' "
         + "AND shelf_num = '" + shelf_num + "' "
         + "ORDER BY shelf_stock.date_recorded DESC LIMIT 1" )
      if cursor.rowcount > 0:
        last_value[shelf_num] = cursor.fetchone()[0]
      # if no last_value found
      else:
        last_value[shelf_num] = 0
      #sys.stdout.write("LOOKUP last_value["+shelf_num+"]="+str( last_value[shelf_num] )+">>>>>"+str(cursor.fetchone()[0])+"\n")

    #calculate analytics
    low_stock = True if detectionDetails["PercentFull"] < .4 else False
    cursor.execute(
    #sys.stdout.write(
      "\nINSERT INTO shelf_stock (racknum, shelf_num, raw_output, triangles_found, triangles_expected, percent_full, date_recorded, url, low_stock, delta) VALUES " +
      "('" + rackNum 
      + "','" + shelf_num
      + "','" + json.dumps( detectionDetails )
      + "','" + str( detectionDetails["TriangleCount"] )
      + "','" + str( detectionDetails["Parameters"]["TrianglesExpected"] )
      + "','" + str( detectionDetails["PercentFull"] )
      + "','" + dateString
      + "','" + aws + path + "/" + filename 
      + "','" + str( low_stock )
      + "','" + str( detectionDetails["PercentFull"] - float(last_value[shelf_num] )) + "')\n" )
    sys.stdout.write(".")
    sys.stdout.flush()
    #sys.stdout.write(str(shelf_num)+":"+str(date_recorded)+"-"+str( detectionDetails["PercentFull"] )+"\n")
    #sys.stdout.write(str(shelf_num)+":"+str(date_recorded)+" last_value["+shelf_num+"]="+str( last_value[shelf_num] )+"-"+str( detectionDetails["PercentFull"] )+"=  "+str( detectionDetails["PercentFull"] - last_value[shelf_num] )+"\n")
    # record last value
    last_value[shelf_num] = detectionDetails["PercentFull"]
    conn.commit()

  cursor.close()
  conn.close()
  #sys.stdout.write("\n")

def usage():
    print("python processrackimages.py -r 000000 -d YYYY-MM-DD")
    print("  -r 000000 : unique rack ID number")
    print("  -d YYYY-MM-DD : UTC date ex: 2016-11-28")

# call main function
if __name__ == "__main__":
    main(sys.argv[1:])

