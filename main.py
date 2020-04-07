import requests
import sys
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Retrieve and Tabularize Bluetooth GATT Characteristics or Services')
parser.add_argument('type', choices=['characteristics', 'services', 'all'], help='Whether to retrieve characteristics, services, or both')
# parser.add_argument('--format', default='md', choices=['md', 'csv']) # TODO: Output CSV
parser.add_argument('--outfile', type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

# Constants. Change if URLs change
root = 'https://www.bluetooth.com'
headers = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

svc_table = '/specifications/gatt/services/'
chr_table = '/specifications/gatt/characteristics/'

characteristics = []
services = []

if args.type == 'characteristics' or args.type == 'all':
    page = requests.get(root+chr_table, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    for row in soup.find_all('tr'):
        # Skip header
        if row.find('th'):
            continue

        link = row.find('a')
        if link:
            chr_name = link.text

            # Set up xml parsing
            xml_url = link['href'].split('src=')[0]
            xml = requests.get(xml_url, headers=headers)

            x_soup = BeautifulSoup(xml.text, 'lxml')

            xml_name = x_soup.find('characteristic')['name']
            if xml_name != chr_name:
                print('Differing names: xml: {}, link: {}'.format(xml_name, chr_name), file=sys.stderr)

            # Remove newlines, replace bullet points with hyphens.
            description = ''
            if x_soup.find('informativetext'):
                description = x_soup.find('informativetext').get_text(' ', strip=True)
                description = ''.join(description.splitlines())
                description = description.replace('â\x80¢', '-')
                description = description.replace('â', '"')
                description = description.replace('â', '"')
            else:
                print('No description for {}'.format(chr_name), file=sys.stderr)

            fields = []
            for field in x_soup.find_all('field'):
                fields.append(field['name'])


            characteristic = {}
            characteristic['name'] = chr_name
            characteristic['description'] = description
            characteristic['fields'] = fields
            characteristics.append(characteristic)

        else:
            chr_name = row.contents[1].get_text()
            print('No link for {}'.format(chr_name), file=sys.stderr)
            characteristic = {}
            characteristic['name'] = chr_name
            characteristics.append(characteristic)

if args.type == 'services' or args.type == 'all':

    page = requests.get(root+svc_table, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')


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
                print('Differing names: xml: {}, link: {}'.format(xml_name, service_name), file=sys.stderr)

            # Remove newlines, replace bullet points with hyphens.
            description = x_soup.find('informativetext').get_text(' ', strip=True)
            description = ''.join(description.splitlines())
            description = description.replace('â\x80¢', '-')
            description = description.replace('â', '"')
            description = description.replace('â', '"')

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
            svc_name = row.contents[1].get_text()
            print('No link for {}'.format(svc_name), file=sys.stderr)
            service = {}
            service['name'] = svc_name
            services.append(service)

if args.type == 'characteristics' or args.type == 'all':
    args.outfile.write('| Characteristic Name | Description | Fields\n')
    args.outfile.write('|---\n')
    for characteristic in characteristics:
        args.outfile.write(u'| {} | {} | {}\n'.format(
            characteristic.get('name', 'Not Available'), 
            characteristic.get('description', 'Not Available'), 
            ', '.join(characteristic.get('fields', ['Not Available']))
            ))

if args.type == 'services' or args.type == 'all':
    args.outfile.write('| Service Name | Description | Mandatory Characteristics | Optional Characteristics\n')
    args.outfile.write('|---\n')
    for service in services:
        args.outfile.write(u'| {} | {} | {} | {}\n'.format(
            service.get('name', 'Not Available'), 
            service.get('description', 'Not Available'), 
            ', '.join(service.get('mandatory', ['Not Available'])), 
            ', '.join(service.get('optional', ['Not Available']))
            ))
