import subprocess
import getopt
import sys
from datetime import date, timedelta

RACKS = ('000102')
log = ''''''
def main(argv):
    global log
    # set default date to yesterday
    yesterday = date.today() - timedelta(1)
    subjectDate = yesterday.strftime('%Y-%m-%d')
    dateParts = subjectDate.split("-")
    subjectYear = dateParts[0]
    subjectMonth = dateParts[1]
    subjectDay = dateParts[2]
    # parse commandline parameters
    try:
        opts, args = getopt.getopt(argv, "d:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if opts is None:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-d':
            subjectDate = arg
            dateParts = subjectDate.split("-")
            subjectYear = dateParts[0]
            subjectMonth = dateParts[1]
            subjectDay = dateParts[2]
            if len(dateParts) != 3 or len(subjectYear) != 4 or len(subjectMonth) != 2 or len(subjectDay) != 2:
                print("Invalid date")
                usage()
                sys.exit(2)
    log += 'Processing For Date '+subjectDate+'\n'
    for rack in RACKS:
        log += '**************\n'
        log += 'Processing Rack '+rack+'\n'
        command = '''python processrackimages.py -r {0} -d {1}'''.format( rack, subjectDate)
        print('\n' + 'Processing Rack '+rack)
        log += '---------\n'
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            output, err = process.communicate()
            log += str(output)
            print(output)
            process.wait()
        except subprocess.TimeoutExpired:
            pass

        log += '\n-------\\------\n'

    create_log(subjectDate)
def usage():
    print("python custom_process.py -d YYYY-MM-DD")
    print("  -d YYYY-MM-DD : UTC date ex: 2016-11-28")

def create_log(date):
    path = "./logs/"+date+".txt"
    f = open(path, "w+")
    f.write(log)
    f.close()

# call main function
if __name__ == "__main__":
    main(sys.argv[1:])
