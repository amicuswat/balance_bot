import os
import time

import requests
from dotenv import load_dotenv


def main(api_key, url):
    params = {
        'api_key': api_key
    }

    while True:
        response = requests.get(url, params=params)
        print(response.json()['balance'])

        params = {
            "amount":10
        }


        response = requests.post('http://localhost:8000/api/v1/balancelist/', json=params)
        print(response.json())
        time.sleep(60)


if __name__ == "__main__":
    load_dotenv()

    api_key = os.environ['FRIGAT_API_KEY']
    url = 'https://frigate-proxy.ru/ru/api/balance'

    main(api_key, url)
