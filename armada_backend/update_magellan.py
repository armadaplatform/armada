import requests
import json
import traceback


def main():
    url = 'http://localhost/list?microservice_name=magellan'
    try:
        response = requests.get(url)
        output = response.json()
        if output['status'] == 'ok':
            address = output['result'][0]['address']
            update_url = 'http://{}/update'.format(address)
            update_response = requests.get(update_url)
            update_response.raise_for_status()
    except:
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
