from ast import parse
import time
import json
import subprocess

from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


def get_dell_serial():
    try:
        result = subprocess.run(['wmic', 'bios', 'get', 'serialnumber'], stdout=subprocess.PIPE)
        return result.stdout
    except:
        print('No serial found')
        exit()


def parse_driver_list(page_requests):
    for request in page_requests:
        if request.response:
            if request.url.__contains__('fetchdriversbytag'):
                driver_data = json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')))
                
    drivers = dict()
    for item in driver_data['DriverListData']:
        if not drivers.keys().__contains__(item['Type']):
            drivers[item['Type']] = list()
    
        drivers[item['Type']].append({item['DriverName']: item['FileFrmtInfo']['HttpFileLocation']})
    
    return drivers


DELL_SERIAL = get_dell_serial()
DRIVER_URL = 'https://www.dell.com/support/home/en-uk/product-support/servicetag/%s/drivers' % DELL_SERIAL


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options=options)
    driver.get(DRIVER_URL)

    print('Validating session, please wait..')
    WebDriverWait(driver, 60).until_not(expected_conditions.title_contains('Challenge Validation'))
    print('Session validated!')

    time.sleep(3)

    drivers = parse_driver_list(driver.requests)

    print(drivers)
