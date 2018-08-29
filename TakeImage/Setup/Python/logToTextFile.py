import subprocess
import time
import datetime

# Delay in minutes
logDelay = 1

def writeTofile(line):
    with open("piData.csv", "a") as w:
        w.write(line)

if __name__ == '__main__':
    while True:
        # Gettting Ip address of the pi
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )

        # Wifi connection Strength
        cmd = "iwconfig wlan0 | grep -i --color quality"
        wifiStrength = subprocess.check_output(cmd, shell = True )

        # Cpu Usage
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True )

        # Memory Usage
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )

        # DiskUsage
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True )

        cmd = "cpu=$(</sys/class/thermal/thermal_zone0/temp) | printf $((cpu/1000))"
        CPUTemp = subprocess.check_output(cmd, shell = True )

        # Current date and time
        dateTime = datetime.datetime.now()
        IP       = IP.decode().rstrip()

        Strength = wifiStrength.decode().rstrip().lstrip()
        Cpu      = CPU.decode()
        MemUsage = MemUsage.decode()
        Disk     = Disk.decode()
        CPUTemp  = CPUTemp.decode()
        line     = str(dateTime) + ", " + IP +", "+ Strength + ", " + Cpu + ", " + CPUTemp + ", " + Disk +"\n"

        print(line)
        writeTofile(line)

        time.sleep(logDelay * 60 )