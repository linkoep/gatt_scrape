# Bluetooth GATT Service Scraper
Scrapes through the [Bluetooth GATT Service XMLs](https://www.bluetooth.com/specifications/gatt/services/) and outputs service names,
	descriptions, and required and optional characteristics as a
	markdown-compatible table. For (slightly) more details and example
	output see [my
	website](https://linuskoepfer.dev/projects/gatt-scraper/)
## Usage
```
main.py [-h] [--outfile OUTFILE] {characteristics,services,all}
```
For example:
```
$ python3 main.py --outfile gatt-svcs.md services
```
Mismatches between link name and XML name, and rows with no links are printed to stderr.
