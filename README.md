# Maidenhead Grid Square Contest Map Generator

A Python tool that creates color-coded maps of Maidenhead grid squares from amateur radio contest logs, showing geographic coverage and contact density by frequency band.

## Features

- **Multi-band Analysis**: Creates separate maps for each frequency band found in the log
- **Accurate Grid Visualization**: Renders actual grid square boundaries (2° × 1° for 4-character, 5' × 2.5' for 6-character grids)
- **Field Labels**: Displays 2-letter grid field designators (EM, EN, EL, etc.) on the map
- **Contact Density**: Color-coded intensity showing number of contacts per grid square
- **Cabrillo Format Support**: Parses standard Cabrillo contest log files
- **Americas Coverage**: Optimized for North and South American contest activity

## Sample Output

The tool generates high-resolution PNG maps showing:
- Grid squares as colored rectangles with actual geographic boundaries
- Color intensity indicating contact density (light red = few contacts, dark red = many contacts)
- Grid field labels for easy reference
- Callsign and band information in the title
- Geographic features (coastlines, borders, land/ocean)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/maidenhead-contest-maps.git
cd maidenhead-contest-maps
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python maidenhead_map.py your_contest_log.cbr
```

The script will:
1. Parse your Cabrillo log file
2. Extract grid squares and frequency information
3. Create separate maps for each band
4. Save maps as `CALLSIGN_BAND_maidenhead_map.png`

### Example Output Files
- `K1TO_6m_maidenhead_map.png` - 6-meter band contacts
- `K1TO_2m_maidenhead_map.png` - 2-meter band contacts
- `K1TO_70cm_maidenhead_map.png` - 70cm band contacts

## Supported Bands

- **6m** (50 MHz)
- **2m** (144 MHz) 
- **1.25m** (222 MHz)
- **70cm** (432 MHz)
- **33cm** (902/903 MHz)
- **23cm** (1296 MHz)

## Requirements

- Python 3.7+
- matplotlib
- cartopy
- numpy (installed with matplotlib)

## File Format

The tool expects standard Cabrillo format contest logs with:
- `CALLSIGN:` header line
- `QSO:` lines containing frequency and grid square exchanges

Example QSO line:
```
QSO:      50 DG 2025-09-13 1801 K1TO              EL87   WA4GPM            EM90
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Uses Natural Earth data for geographic features
- Built with matplotlib and cartopy for mapping
- Designed for amateur radio VHF/UHF contest analysis
