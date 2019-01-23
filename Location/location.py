import requests
import json
import subprocess

racknum = "000109"
local = "192.168.0.108:3001"
online = "smartrackapi.herokuapp.com"
used_host = online
api_server = "http://" + used_host + "/location/api/location/" + racknum
url = "https://www.googleapis.com/geolocation/v1/geolocate?key="
key = "Your_Key"
command = 'sudo iwlist wlan0 scanning | egrep "Signal level|Address" | sed -e "s/\tAddress //" -e "s/\tQuality //" | awk \'{ORS = (NR % 2 == 0)? "\\n" : " "; print}\' | sort'

def get_wifi_list():
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
    wifi_signals = []
    for line in process.stdout:
        indx_addr = line.find('Address:', 0)
        indx_Signal = line.find('level=', 0)
        mac_address = line[indx_addr + 9: indx_addr + 9 + 18].strip()
        signal_strength = line[indx_Signal + 6: indx_Signal + 6 + 4].strip()
        wifi_signals.append({"macAddress": mac_address, "signalStrength": int(signal_strength)})
         #print(mac_address + ' -> ' + signal_strength)
    return wifi_signals


def get_location(json_data):
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Arduino/1.0'}
    r = requests.post(url + key, data=json.dumps(json_data), headers=headers)
    print("Location: ")
    print(r.text)
    return r


def save_location(location):
    #print("Location: ", location)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(api_server, data=location, headers=headers)
    #print(r.text)


def main():
    wifi_signals = get_wifi_list()
    #print(wifi_signals)
    json_data = {
        "wifiAccessPoints": wifi_signals
    }
    location = get_location(json_data)
    save_location(location)


# call main function
if __name__ == "__main__":
    main()


