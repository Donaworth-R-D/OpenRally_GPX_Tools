import argparse
import xml.etree.ElementTree as ET
import base64
from io import BytesIO
from PIL import Image
from fpdf import FPDF
import tempfile
import os

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Convert OpenRally GPX to enhanced PDF roadbook.')
parser.add_argument('gpx_file', help='Input GPX file')
args = parser.parse_args()

# Parse GPX file
gpx_file = args.gpx_file
tree = ET.parse(gpx_file)
root = tree.getroot()
ns = {
    'gpx': 'http://www.topografix.com/GPX/1/1',
    'openrally': 'http://www.openrally.org/xmlschemas/GpxExtensions/v1.0.3'
}

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Rally Roadbook', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def add_waypoint_table_row(self, cumulative_km, incremental_km, waypoint_num, cap, tulip_img, notes_img, coords):
        row_height = 50
        col1_width = 30  # Main nav cell
        col2_width = 70  # Tulip
        col3_width = 70  # Notes/img
        col4_width = 0  # (Unused, but you can adjust for more columns)

        if self.get_y() + row_height > 270:
            self.add_page()
        start_y = self.get_y()

        # Draw main cell border
        self.rect(10, start_y, col1_width, row_height)

        # Cumulative km (top, centered)
        self.set_xy(10, start_y + 3)
        self.set_font('Arial', 'B', 24)
        self.cell(col1_width, 12, f'{cumulative_km:.2f}', 0, 2, 'C')

        # Incremental km (bottom left, small cell)
        inc_cell_w, inc_cell_h = 15, 10
        inc_x = 10
        inc_y = start_y + row_height - inc_cell_h - 2
        self.rect(inc_x, inc_y, inc_cell_w, inc_cell_h)
        self.set_xy(inc_x, inc_y + 2)
        self.set_font('Arial', '', 9)
        self.cell(inc_cell_w, 6, f'{incremental_km:.2f}', 0, 0, 'C')

        # Waypoint num (bottom right, small cell, black background, white text)
        num_cell_w, num_cell_h = 10, 10
        num_x = 10 + col1_width - num_cell_w
        num_y = inc_y
        self.set_fill_color(0, 0, 0)      # Black background
        self.set_text_color(255, 255, 255)  # White text
        self.rect(num_x, num_y, num_cell_w, num_cell_h, style='F')  # Filled rectangle
        self.set_xy(num_x, num_y + 2)
        self.set_font('Arial', 'B', 10)
        self.cell(num_cell_w, 6, str(waypoint_num), 0, 0, 'C')
        self.set_fill_color(255, 255, 255)  # Reset fill color to white
        self.set_text_color(0, 0, 0)        # Reset text color to black

        # Tulip cell
        self.rect(10 + col1_width, start_y, col2_width, row_height)
        if tulip_img:
            try:
                img_data = base64.b64decode(tulip_img.split(',')[1])
                img = Image.open(BytesIO(img_data))
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    img.save(tmp_file.name, format='PNG')
                    self.image(tmp_file.name, x=10 + col1_width + 2, y=start_y + 5, w=col2_width - 4, h=row_height - 10)
                    os.unlink(tmp_file.name)
            except Exception as e:
                print(f"Error processing tulip image: {e}")

        # Notes/img cell
        notes_x = 10 + col1_width + col2_width
        self.rect(notes_x, start_y, col3_width, row_height)
        if notes_img:
            try:
                img_data = base64.b64decode(notes_img.split(',')[1])
                img = Image.open(BytesIO(img_data))
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    img.save(tmp_file.name, format='PNG')
                    self.image(tmp_file.name, x=notes_x + 2, y=start_y + 5, w=col3_width - 24, h=row_height - 14)
                    os.unlink(tmp_file.name)
            except Exception as e:
                print(f"Error processing notes image: {e}")

        # Coords cell (bottom right of notes cell)
        coords_cell_w, coords_cell_h = 22, 10
        coords_x = notes_x + col3_width - coords_cell_w - 2
        coords_y = start_y + row_height - coords_cell_h - 2
        self.rect(coords_x, coords_y, coords_cell_w, coords_cell_h)
        self.set_xy(coords_x, coords_y + 2)
        self.set_font('Arial', '', 7)
        self.multi_cell(coords_cell_w, 4, coords, 0, 'C')

        # CAP (optional, under cumulative_km)
        if cap:
            self.set_xy(10, start_y + 15)
            self.set_font('Arial', '', 9)
            self.cell(col1_width, 6, f'CAP: {cap}°', 0, 0, 'C')

        # Move to next row
        self.set_y(start_y + row_height)

# Create PDF
pdf = PDF()
pdf.add_page()

# Extract waypoints and calculate totals
waypoints = []
cum_km = 0.0
prev_cum_km = 0.0

for wpt in root.findall('gpx:wpt', ns):
    name_elem = wpt.find('gpx:name', ns)
    num = name_elem.text if name_elem is not None else ''
    lat_str = wpt.get('lat')
    lon_str = wpt.get('lon')
    if lat_str is None or lon_str is None:
        continue  # Skip this waypoint if coordinates are missing
    lat = float(lat_str)
    lon = float(lon_str)
    
    ext = wpt.find('gpx:extensions', ns)
    
    if ext is not None:
        dist_tag = ext.find('openrally:distance', ns)
        if dist_tag is not None and dist_tag.text is not None:
            cum_km = float(dist_tag.text)
        else:
            cum_km = 0.0   # cumulative from GPX
        cap = ext.find('openrally:cap', ns)
        cap_value = cap.text if cap is not None else ''
        tulip = ext.find('openrally:tulip', ns)
        tulip_img = tulip.text.strip() if tulip is not None and tulip.text is not None else None
        notes = ext.find('openrally:notes', ns)
        notes_img = notes.text.strip() if notes is not None and notes.text is not None else None
    else:
        cum_km = 0.0
        cap_value = ''
        tulip_img = None
        notes_img = None
    incr_km = cum_km - prev_cum_km                                   # incremental distance
    prev_cum_km = cum_km                                             # update for next loop
    
    # Format coordinates
    lat_deg = int(lat)
    lat_min = (lat - lat_deg) * 60
    lat_dir = 'N' if lat >= 0 else 'S'
    
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_dir = 'E' if lon >= 0 else 'W'
    
    coords = f"{abs(lat_deg)}°{lat_min:.3f}'{lat_dir}\n{lon_deg}°{lon_min:.3f}'{lon_dir}"
    
    waypoints.append({
        'num': num,
        'cumulative_km': cum_km,
        'incremental_km': incr_km,
        'cap': cap_value,
        'tulip_img': tulip_img,
        'notes_img': notes_img,
        'coords': coords
    })

# Add waypoint table rows
for wpt in waypoints:
    pdf.add_waypoint_table_row(
        cumulative_km=wpt['cumulative_km'],
        incremental_km=wpt['incremental_km'],
        waypoint_num=wpt['num'],
        cap=wpt['cap'],
        tulip_img=wpt['tulip_img'],
        notes_img=wpt['notes_img'],
        coords=wpt['coords']
    )

# Output PDF
pdf_filename = os.path.splitext(os.path.basename(gpx_file))[0] + '.pdf'
pdf.output(pdf_filename)
print('Enhanced roadbook PDF generated successfully!')