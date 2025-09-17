# Maidenhead Grid Square Contest Map Generator

A Python tool that creates color-coded maps of Maidenhead grid squares from amateur radio contest logs, showing geographic coverage and contact density by frequency band.

## Features

- **Multi-format Support**: Supports both Cabrillo (.cbr/.log) and CSV (.csv) file formats
- **Multi-band Analysis**: Creates separate maps for each frequency band found in the log
- **Automatic Continent Detection**: Auto-selects continents based on grid squares in the log
- **Manual Continent Selection**: Choose specific continents to display
- **Accurate Grid Visualization**: Renders actual grid square boundaries (2° × 1° for 4-character, 5' × 2.5' for 6-character grids)
- **Field Labels**: Displays 2-letter grid field designators (EM, EN, EL, etc.) on the map
- **Contact Density**: Color-coded intensity showing number of contacts per grid square
- **Global Coverage**: Supports all continents with optimized map bounds

## Sample Output

The tool generates high-resolution PNG maps showing:
- Grid squares as colored rectangles with actual geographic boundaries
- Color intensity indicating contact density (light red = few contacts, dark red = many contacts)
- Grid field labels for easy reference
- Callsign and band information in the title
- Geographic features (coastlines, borders, land/ocean)
- Automatic map bounds based on selected continents

## Installation

1. Clone this repository:
```bash
git clone https://github.com/rushealy-aws/grid-mapper.git
cd grid-mapper
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

### Basic Usage
```bash
python maidenhead_map.py your_contest_log.cbr
python maidenhead_map.py your_contest_log.csv
```

### Specify Continents
```bash
python maidenhead_map.py your_log.csv --continents north_america europe
python maidenhead_map.py your_log.cbr --continents asia oceania
```

### Available Continents
- `north_america` - North America
- `south_america` - South America  
- `europe` - Europe
- `africa` - Africa
- `asia` - Asia
- `oceania` - Australia and Pacific Islands

### File Format Support

#### Cabrillo Format (.cbr, .log)
Standard Cabrillo contest logs with QSO lines:
```
QSO:      50 DG 2025-09-13 1801 K1TO              EL87   WA4GPM            EM90
```

#### CSV Format (.csv)
CSV files with columns for callsign, frequency/band, and grid squares:
```csv
callsign,freq,grid,date,time
K1TO,50,EL87,2025-09-13,1801
WA4GPM,50,EM90,2025-09-13,1801
```

The script automatically detects common CSV column names:
- **Frequency**: freq, frequency, band, freq_mhz
- **Grid**: grid, gridsquare, grid_square, their_grid, dx_grid
- **Callsign**: call, callsign, station_callsign, my_call

## Output Files

The script creates separate maps for each band with descriptive filenames:
- `K1TO_6m_north_america_maidenhead_map.png` - 6m band, North America
- `K1TO_2m_europe_asia_maidenhead_map.png` - 2m band, Europe and Asia
- `K1TO_70cm_world_maidenhead_map.png` - 70cm band, worldwide

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

## Examples

### Example 1: Auto-detect continents from Cabrillo log
```bash
python maidenhead_map.py contest_log.cbr
```

### Example 2: CSV file with specific continents
```bash
python maidenhead_map.py my_log.csv --continents north_america south_america
```

### Example 3: European contest
```bash
python maidenhead_map.py eu_contest.csv --continents europe
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
- Supports worldwide amateur radio activity mapping
