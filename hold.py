

import requests
import time

url = "contemporary-bonni-akkkkfvbnbdtlpo466u-ad416e1d.koyeb.app/"

while True:
    try:
        response = requests.get(url)
        print("Status Code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
    
    time.sleep(20)
