import xml.etree.ElementTree as ET
import argparse
import os

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Convert OpenRally GPX to Waypoint GPX file.')
parser.add_argument('gpx_file', help='Input GPX file')
args = parser.parse_args()

# Parse GPX file
gpx_file = args.gpx_file
tree = ET.parse(gpx_file)
root = tree.getroot()
ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

# Create a new GPX root
gpx_out = ET.Element('gpx', attrib={
    'version': '1.1',
    'creator': 'ADV-TIM LLC',
    'xmlns': 'http://www.topografix.com/GPX/1/1'
})

# Copy waypoints
for wpt in root.findall('gpx:wpt', ns):
    lat = wpt.get('lat') or ''
    lon = wpt.get('lon') or ''
    name_elem_obj = wpt.find('gpx:name', ns)
    name = name_elem_obj.text if name_elem_obj is not None else ''
    wpt_out = ET.SubElement(gpx_out, 'wpt', attrib={'lat': lat, 'lon': lon})
    name_elem = ET.SubElement(wpt_out, 'name')
    name_elem.text = name

# Write to file
base_name = os.path.splitext(os.path.basename(gpx_file))[0]
output_filename = f"{base_name}_waypoint.gpx"
tree_out = ET.ElementTree(gpx_out)
tree_out.write(output_filename, encoding='utf-8', xml_declaration=True)
print(f'{output_filename} generated!')