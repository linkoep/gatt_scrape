import requests
from bs4 import BeautifulSoup

# Set up table parsing
root = 'https://www.bluetooth.com'
table_url = '/specifications/gatt/services/'
headers = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
page = requests.get(root+table_url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')

# list to populate
services = []

for row in soup.find_all('tr'):
    # Skip header
    if row.find('th'):
        continue


    link = row.find('a')
    if link:
        service_name = link.text

        # Set up xml parsing
        xml_url = link['href']
        xml = requests.get(root+xml_url, headers=headers)

        x_soup = BeautifulSoup(xml.text, 'lxml')

        xml_name = x_soup.find('service')['name']
        if xml_name != service_name:
            print('xml: {}, link: {}'.format(xml_name, service_name))

        description = x_soup.find('informativetext').text
        mandatory = []
        optional = []
        for characteristic in x_soup.find_all('characteristic'):
            if characteristic.requirement.text == 'Mandatory':
                mandatory.append(characteristic['name'])
            else:
                optional.append(characteristic['name'])

        service = {}
        service['name'] = service_name
        service['description'] = description
        service['mandatory'] = mandatory
        service['optional'] = optional
        services.append(service)

    else:
        print(row)

# Make markdown table
print('| Service Name | Description | Mandatory Characteristics | Optional Characteristics')
print('|---')
for service in services:
    print('| {} | {} | {} | {}'.format(
        service['name'], 
        service['description'], 
        ','.join(service['mandatory']), 
        ','.join(service['optional'])
        ))



