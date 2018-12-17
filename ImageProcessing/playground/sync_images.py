import sys
import getopt
import json
import subprocess
import os
import psycopg2
from datetime import date, timedelta
import time
import os, sys, shutil
from os import path

basket_num = 1
bucket_name = 'smart-basket-itcus'
path = basket_num + '/2018'
def main(argv):
    command = "aws s3 sync s3://" + bucket_name + "/ ./temp/basket"
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait(10)
    except subprocess.TimeoutExpired:
        pass