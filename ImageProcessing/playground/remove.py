import shutil
#shutil.rmtree('/temp/s3')

def create_log(date):
    path = "./logs/"+date+".txt"
    f = open(path, "w+")
    f.write('''Helllo Friends Chai Peelo''')
    f.close()

#create_log("2018-06-12")

racks = ('001', '002')
r = "Racks Are " + str(racks)
print(r)