import requests
import json
settings = {}

def main():
    with open('settings.json') as jsonData:
      settings = json.load(jsonData)
      print(settings)
      jsonData.close()

    for a in range(0, 30):
        url = settings['server']['local'] + "/shelves/api/restock/generate/"+str(a)
        response = requests.request("GET", url)
        print(a)
        print(response.status_code)
        if response.status_code == '200':
            print("Generated restock response for yesterday : " + a)

# call main function
if __name__ == "__main__":
    main()