import subprocess
import getopt
import sys
from datetime import date, timedelta

RACKS = ('001', '002')


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
        opts, args = getopt.getopt(argv, "s:")
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

    for rack in RACKS:
        command = '''python processrackimages.py -r {0} -d {1}'''.format( rack, subjectDate)
        print('\n' + 'Processing Rack '+rack)
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()
        except subprocess.TimeoutExpired:
            pass


def usage():
    print("python custom_process.py -d YYYY-MM-DD")
    print("  -d YYYY-MM-DD : UTC date ex: 2016-11-28")


# call main function
if __name__ == "__main__":
    main(sys.argv[1:])
