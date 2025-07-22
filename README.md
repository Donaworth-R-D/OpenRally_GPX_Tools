# TarraPirata (OpenRally) GPX to PDF Roadbook Tools

This repository contains two Python scripts for working with Open Rally GPX Roadbook files and generating rally-style roadbooks in PDF format.

## Scripts Overview

### `openrally_to_pdf.py`
- **Purpose:**  
  Parses a GPX file with OpenRally extensions and generates a detailed rally roadbook as a PDF.  
  Each waypoint is rendered as a table row with cumulative and incremental distances, CAP heading, tulip diagram, notes image, and formatted coordinates.

- **Features:**  
  - Reads GPX waypoints and extracts relevant OpenRally data.
  - Decodes embedded base64 images for tulip and notes.
  - Formats and lays out each waypoint in a printable PDF.
  - **Outputs a file named `{input_name}.pdf`, where `{input_name}` is the input GPX filename without extension.**

### `openrally_to_waypoint.py`
- **Purpose:**  
  Extracts all waypoints from a GPX file and writes them to a new GPX file.  
  Useful for creating a simplified GPX containing only waypoints.

- **Features:**  
  - Parses the input GPX file.
  - Copies all waypoints (with names) to a new GPX structure.
  - **Outputs a file named `{input_name}_waypoint.gpx`, where `{input_name}` is the input GPX filename without extension.**

## Requirements

- Python 3.x
- [fpdf2](https://pypi.org/project/fpdf2/)
- [Pillow](https://pypi.org/project/Pillow/)

Install dependencies with:
```sh
pip install fpdf2 Pillow
```

## Usage

### 1. Generate a Roadbook PDF

Run the script with your GPX file as an argument:

```sh
python openrally_to_pdf.py yourfile.gpx
```

The script will create `yourfile.pdf` in the current directory.

### 2. Extract Waypoints to a New GPX

Run the script with your GPX file as an argument:

```sh
python openrally_to_waypoint.py yourfile.gpx
```

The script will create `yourfile_waypoint.gpx` in the current directory.

## Files

- `openrally_to_pdf.py` — Generate a rally roadbook PDF from an OpenRally GPX file.
- `openrally_to_waypoint.py` — Extract waypoints from an OpenRally GPX file to a new GPX.

## License

MIT License. See [LICENSE](LICENSE) for details.