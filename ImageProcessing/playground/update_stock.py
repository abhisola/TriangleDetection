import subprocess
import psycopg2
from datetime import date, timedelta
import json
import sys
import getopt

with open('../settings.json') as jsonData:
  settings = json.load(jsonData)
  jsonData.close()

hostname = settings['postgres']['hostname']
username = settings['postgres']['username']
password = settings['postgres']['password']
database = settings['postgres']['database']
aws = settings['s3']['url']

# main program entry point - decode parameters, act accordingly
def main(argv):
    # setup DB
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = conn.cursor()
    selectRows = 'Select url, shid from shelf_stock order by shid asc'
    cursor.execute(selectRows)
    if cursor.rowcount > 0:
        rows = cursor.fetchall()
        for row in rows:
            print('Found Row: '+str(row))
            url = row[0]
            shid = row[1]
            if 'my-rack' in url:
                url = url.replace('my-rack', 'smart-rack-bucket')
                print('Url Changed: '+url)
                update_row = "Update shelf_stock set url='"+url+"' where shid="+str(shid)
                print('Updating : '+update_row)
                cursor.execute(update_row)
                conn.commit()
                if cursor.rowcount > 0:
                    print('Row '+str(shid)+' Updated Successfully')
                else:
                    print('Row '+str(shid)+' Couldnot Be Updated')
            else:
                print('Row '+str(shid)+' Is already updated')
    # if no last_value found
    else:
        print('Nothing Happened')
    
    cursor.close()
    conn.close()
  # call main function
if __name__ == "__main__":
    main(sys.argv[1:])
