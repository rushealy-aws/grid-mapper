#!/usr/bin/env python3
import re
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from collections import Counter, defaultdict

# Continent boundaries (approximate)
CONTINENT_BOUNDS = {
    'north_america': {'lat': (10, 85), 'lon': (-180, -30)},
    'south_america': {'lat': (-60, 15), 'lon': (-90, -30)},
    'europe': {'lat': (35, 75), 'lon': (-15, 45)},
    'africa': {'lat': (-40, 40), 'lon': (-20, 55)},
    'asia': {'lat': (5, 80), 'lon': (25, 180)},
    'oceania': {'lat': (-50, 0), 'lon': (110, 180)}
}

def maidenhead_to_bounds(grid):
    """Convert Maidenhead grid square to lat/lon bounds"""
    grid = grid.upper().strip()
    
    lon_base = (ord(grid[0]) - ord('A')) * 20 - 180
    lat_base = (ord(grid[1]) - ord('A')) * 10 - 90
    
    if len(grid) >= 4:
        lon_base += int(grid[2]) * 2
        lat_base += int(grid[3]) * 1
        
        if len(grid) == 4:
            return lat_base, lat_base + 1, lon_base, lon_base + 2
        elif len(grid) == 6:
            lon_base += (ord(grid[4]) - ord('A')) * (2/24)
            lat_base += (ord(grid[5]) - ord('A')) * (1/24)
            return lat_base, lat_base + (1/24), lon_base, lon_base + (2/24)
    
    return None

def get_grid_continent(grid):
    """Determine which continent a grid square belongs to"""
    bounds = maidenhead_to_bounds(grid)
    if not bounds:
        return None
    
    lat_min, lat_max, lon_min, lon_max = bounds
    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2
    
    for continent, bounds in CONTINENT_BOUNDS.items():
        if (bounds['lat'][0] <= lat_center <= bounds['lat'][1] and 
            bounds['lon'][0] <= lon_center <= bounds['lon'][1]):
            return continent
    
    return 'other'

def parse_csv_grids(filename):
    """Extract Maidenhead grid squares by band from CSV format file"""
    grids_by_band = defaultdict(list)
    callsign = "Unknown"
    
    try:
        with open(filename, 'r') as f:
            # Try to detect CSV format
            sample = f.read(1024)
            f.seek(0)
            
            # Look for common CSV headers
            reader = csv.DictReader(f)
            headers = [h.lower() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Common field mappings
            freq_fields = ['freq', 'frequency', 'band', 'freq_mhz']
            grid_fields = ['grid', 'gridsquare', 'grid_square', 'their_grid', 'dx_grid']
            call_fields = ['call', 'callsign', 'station_callsign', 'my_call']
            
            freq_field = next((f for f in freq_fields if f in headers), None)
            grid_field = next((f for f in grid_fields if f in headers), None)
            call_field = next((f for f in call_fields if f in headers), None)
            
            f.seek(0)
            reader = csv.DictReader(f)
            
            for row in reader:
                # Extract callsign if available
                if call_field and callsign == "Unknown":
                    callsign = row[call_field].strip()
                
                # Extract frequency/band
                band = "Unknown"
                if freq_field:
                    freq_val = row[freq_field].strip()
                    if freq_val.isdigit():
                        band = freq_to_band(freq_val)
                    else:
                        band = freq_val
                
                # Extract grid square
                if grid_field:
                    grid = row[grid_field].strip().upper()
                    if is_valid_grid(grid):
                        grids_by_band[band].append(grid)
                
                # Also check all fields for grid patterns if no specific grid field
                if not grid_field:
                    for value in row.values():
                        if value and is_valid_grid(value.strip()):
                            grids_by_band[band].append(value.strip().upper())
                            
    except Exception as e:
        print(f"Error parsing CSV file: {e}")
        return {}, callsign
    
    return dict(grids_by_band), callsign

def parse_cabrillo_grids(filename):
    """Extract Maidenhead grid squares by band from Cabrillo format file"""
    grids_by_band = defaultdict(list)
    callsign = "Unknown"
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('CALLSIGN:'):
                    callsign = line.split(':', 1)[1].strip()
                elif line.startswith('QSO:'):
                    parts = line.split()
                    if len(parts) >= 6:
                        freq = parts[1]
                        band = freq_to_band(freq)
                        
                        # In Cabrillo QSO format, grid squares are typically in the exchange fields
                        # Skip the first 6 fields: QSO:, freq, mode, date, time, mycall
                        # Then look for grids in the remaining exchange fields
                        exchange_fields = parts[6:]
                        
                        for field in exchange_fields:
                            field = field.upper()
                            if is_valid_grid(field):
                                grids_by_band[band].append(field)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}, callsign
    
    return dict(grids_by_band), callsign

def is_valid_grid(grid):
    """Check if string is a valid Maidenhead grid square"""
    if not grid or len(grid) not in [4, 6]:
        return False
    
    grid = grid.upper()
    if len(grid) == 4:
        return (grid[0] in 'ABCDEFGHIJKLMNOPQR' and 
                grid[1] in 'ABCDEFGHIJKLMNOPQR' and 
                grid[2] in '0123456789' and 
                grid[3] in '0123456789')
    elif len(grid) == 6:
        return (grid[0] in 'ABCDEFGHIJKLMNOPQR' and 
                grid[1] in 'ABCDEFGHIJKLMNOPQR' and 
                grid[2] in '0123456789' and 
                grid[3] in '0123456789' and
                grid[4] in 'ABCDEFGHIJKLMNOPQRSTUVWX' and
                grid[5] in 'ABCDEFGHIJKLMNOPQRSTUVWX')
    return False

def freq_to_band(freq_str):
    """Convert frequency string to band name using Cabrillo standard nomenclature"""
    try:
        freq = int(freq_str)
        
        # LF/MF bands
        if 472 <= freq <= 479:
            return "630m"
        elif 1800 <= freq <= 2000:
            return "160m"
        elif 3500 <= freq <= 4000:
            return "80m"
        elif 5330 <= freq <= 5405:
            return "60m"
        elif 7000 <= freq <= 7300:
            return "40m"
        elif 10100 <= freq <= 10150:
            return "30m"
        elif 14000 <= freq <= 14350:
            return "20m"
        elif 18068 <= freq <= 18168:
            return "17m"
        elif 21000 <= freq <= 21450:
            return "15m"
        elif 24890 <= freq <= 24990:
            return "12m"
        elif 28000 <= freq <= 29700:
            return "10m"
        
        # VHF bands
        elif freq == 50 or (50000 <= freq <= 54000):
            return "6m"
        elif freq == 144 or (144000 <= freq <= 148000):
            return "2m"
        elif freq == 222 or (222000 <= freq <= 225000):
            return "1.25m"
        
        # UHF bands
        elif freq == 432 or (420000 <= freq <= 450000):
            return "70cm"
        elif freq in [902, 903] or (902000 <= freq <= 928000):
            return "33cm"
        elif freq == 1296 or (1240000 <= freq <= 1300000):
            return "23cm"
        
        # Microwave bands
        elif 2300000 <= freq <= 2450000:
            return "13cm"
        elif 3300000 <= freq <= 3500000:
            return "9cm"
        elif 5650000 <= freq <= 5925000:
            return "6cm"
        elif 10000000 <= freq <= 10500000:
            return "3cm"
        elif 24000000 <= freq <= 24250000:
            return "1.25cm"
        elif 47000000 <= freq <= 47200000:
            return "6mm"
        elif 75500000 <= freq <= 81000000:
            return "4mm"
        elif 119980000 <= freq <= 120020000:
            return "2.5mm"
        elif 142000000 <= freq <= 149000000:
            return "2mm"
        elif 241000000 <= freq <= 250000000:
            return "1mm"
        
        # Handle frequency in MHz format (common in logs)
        elif freq < 1000:
            if freq == 472:
                return "630m"
            elif freq == 1800 or freq == 1900:
                return "160m"
            elif freq == 3500 or freq == 3700 or freq == 3800:
                return "80m"
            elif freq == 5300:
                return "60m"
            elif freq == 7000 or freq == 7100 or freq == 7200:
                return "40m"
            elif freq == 10100:
                return "30m"
            elif freq == 14000 or freq == 14100 or freq == 14200:
                return "20m"
            elif freq == 18100:
                return "17m"
            elif freq == 21000 or freq == 21100 or freq == 21200:
                return "15m"
            elif freq == 24900:
                return "12m"
            elif freq == 28000 or freq == 28100 or freq == 28200:
                return "10m"
            elif freq == 50:
                return "6m"
            elif freq == 144:
                return "2m"
            elif freq == 222:
                return "1.25m"
            elif freq == 432:
                return "70cm"
            elif freq in [902, 903]:
                return "33cm"
            else:
                return f"{freq}MHz"
        else:
            return f"{freq}kHz"
            
    except ValueError:
        # Handle non-numeric frequency strings
        freq_str = freq_str.upper().strip()
        
        # Direct band name mappings
        band_mappings = {
            '630M': '630m', '160M': '160m', '80M': '80m', '60M': '60m',
            '40M': '40m', '30M': '30m', '20M': '20m', '17M': '17m',
            '15M': '15m', '12M': '12m', '10M': '10m', '6M': '6m',
            '2M': '2m', '1.25M': '1.25m', '70CM': '70cm', '33CM': '33cm',
            '23CM': '23cm', '13CM': '13cm', '9CM': '9cm', '6CM': '6cm',
            '3CM': '3cm', '1.25CM': '1.25cm', '6MM': '6mm', '4MM': '4mm',
            '2.5MM': '2.5mm', '2MM': '2mm', '1MM': '1mm'
        }
        
        return band_mappings.get(freq_str, freq_str)

def auto_select_continents(grids):
    """Automatically determine which continents to include based on grid squares"""
    continents = set()
    for grid in grids:
        continent = get_grid_continent(grid)
        if continent:
            continents.add(continent)
    return list(continents)

def get_optimal_bounds(grids):
    """Calculate optimal map bounds based on actual grid square locations"""
    if not grids:
        return (-180, 180, -90, 90)
    
    lats = []
    lons = []
    
    for grid in grids:
        bounds = maidenhead_to_bounds(grid)
        if bounds:
            lat_min, lat_max, lon_min, lon_max = bounds
            lats.extend([lat_min, lat_max])
            lons.extend([lon_min, lon_max])
    
    if not lats or not lons:
        return (-180, 180, -90, 90)
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Add padding based on the span
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon
    
    # Use smaller padding for regional views
    lat_padding = max(lat_span * 0.15, 2.0)  # At least 2 degrees
    lon_padding = max(lon_span * 0.15, 3.0)  # At least 3 degrees
    
    return (min_lon - lon_padding, max_lon + lon_padding,
            min_lat - lat_padding, max_lat + lat_padding)

def get_region_name(lon_min, lon_max, lat_min, lat_max):
    """Generate a descriptive region name based on bounds"""
    # North America regions
    if -170 <= lon_min and lon_max <= -30 and 10 <= lat_min and lat_max <= 85:
        if lon_min >= -100 and lat_min >= 35:
            return "northeastern_north_america"
        elif lon_min >= -100 and lat_max <= 45:
            return "southeastern_north_america"
        elif lon_max <= -95 and lat_min >= 35:
            return "northwestern_north_america"
        elif lon_max <= -95 and lat_max <= 45:
            return "southwestern_north_america"
        elif lat_min >= 45:
            return "northern_north_america"
        elif lat_max <= 35:
            return "southern_north_america"
        elif lon_min >= -100:
            return "eastern_north_america"
        elif lon_max <= -95:
            return "western_north_america"
        else:
            return "central_north_america"
    
    # Europe regions
    elif -15 <= lon_min and lon_max <= 45 and 35 <= lat_min and lat_max <= 75:
        if lat_min >= 55:
            return "northern_europe"
        elif lat_max <= 50:
            return "southern_europe"
        elif lon_min >= 15:
            return "eastern_europe"
        elif lon_max <= 5:
            return "western_europe"
        else:
            return "central_europe"
    
    # Use continent names for larger areas
    continents = auto_select_continents(list(grid_counts.keys()) if 'grid_counts' in locals() else [])
    if len(continents) == 1:
        return continents[0]
    elif continents:
        return '_'.join(continents)
    else:
        return "regional"

def filter_grids_by_continents(grids, continents):
    """Filter grid squares to only include those in specified continents"""
    if not continents:
        return grids
    
    filtered = {}
    for grid, count in grids.items():
        grid_continent = get_grid_continent(grid)
        if grid_continent in continents:
            filtered[grid] = count
    
    return filtered

def create_grid_map(grids, callsign, band, continents=None, output_file=None):
    """Create color-coded map of Maidenhead grid squares for a specific band"""
    
    grid_counts = Counter(grids)
    
    # Auto-select continents if not specified
    if continents is None:
        continents = auto_select_continents(grids)
        print(f"Auto-selected continents: {', '.join(continents)}")
    
    # Filter grids by continents
    valid_grids = filter_grids_by_continents(grid_counts, continents)
    
    if not valid_grids:
        print(f"No valid grid squares found for {band} in selected continents")
        return
    
    # Get optimal bounds based on actual grid locations
    lon_min, lon_max, lat_min, lat_max = get_optimal_bounds(valid_grids.keys())
    
    # Generate region name based on bounds
    region_name = get_region_name(lon_min, lon_max, lat_min, lat_max)
    
    fig = plt.figure(figsize=(14, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.LAND, alpha=0.2, color='lightgray')
    ax.add_feature(cfeature.OCEAN, alpha=0.2, color='lightblue')
    
    # Plot grid squares as rectangles
    max_count = max(valid_grids.values())
    for grid, count in valid_grids.items():
        bounds = maidenhead_to_bounds(grid)
        if bounds:
            grid_lat_min, grid_lat_max, grid_lon_min, grid_lon_max = bounds
            
            intensity = count / max_count
            color = plt.cm.Reds(0.3 + 0.7 * intensity)
            
            rect = patches.Rectangle((grid_lon_min, grid_lat_min), 
                                   grid_lon_max - grid_lon_min, 
                                   grid_lat_max - grid_lat_min,
                                   linewidth=0.5, 
                                   edgecolor='black', 
                                   facecolor=color,
                                   alpha=0.8,
                                   transform=ccrs.PlateCarree())
            ax.add_patch(rect)
    
    # Add grid field labels - only show if they fit in the visible area
    field_centers = {}
    for grid in valid_grids.keys():
        field = grid[:2]
        if field not in field_centers:
            field_lon_center = (ord(field[0]) - ord('A')) * 20 - 180 + 10
            field_lat_center = (ord(field[1]) - ord('A')) * 10 - 90 + 5
            # Only show labels if they're in the visible area
            if lon_min <= field_lon_center <= lon_max and lat_min <= field_lat_center <= lat_max:
                field_centers[field] = (field_lon_center, field_lat_center)
    
    for field, (lon, lat) in field_centers.items():
        ax.text(lon, lat, field, fontsize=12, fontweight='bold',
                ha='center', va='center', color='blue',
                transform=ccrs.PlateCarree())
    
    ax.gridlines(draw_labels=True, alpha=0.3)
    
    plt.title(f'{callsign} - {band} Band - Maidenhead Grid Squares\n{region_name.replace("_", " ").title()}', 
              fontsize=14, fontweight='bold')
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, 
                               norm=plt.Normalize(vmin=1, vmax=max_count))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6)
    cbar.set_label('Number of Contacts', fontsize=12)
    
    plt.tight_layout()
    
    if not output_file:
        output_file = f"{callsign}_{band}_{region_name}_maidenhead_map.png"
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Map saved as {output_file}")
    print(f"{band}: {len(valid_grids)} unique grid squares, {sum(valid_grids.values())} contacts")

def main():
    """Main entry point for console script"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Maidenhead grid square maps from contest logs')
    parser.add_argument('filename', help='Contest log file (.cbr for Cabrillo, .csv for CSV)')
    parser.add_argument('--continents', nargs='+', 
                       choices=['north_america', 'south_america', 'europe', 'africa', 'asia', 'oceania'],
                       help='Continents to include (auto-detected if not specified)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    filename = args.filename
    
    # Determine file format based on extension
    if filename.lower().endswith('.csv'):
        grids_by_band, callsign = parse_csv_grids(filename)
        print(f"Parsed CSV file: {filename}")
    elif filename.lower().endswith(('.cbr', '.log')):
        grids_by_band, callsign = parse_cabrillo_grids(filename)
        print(f"Parsed Cabrillo file: {filename}")
    else:
        print("Unsupported file format. Use .csv, .cbr, or .log files.")
        sys.exit(1)
    
    if grids_by_band:
        for band, grids in grids_by_band.items():
            create_grid_map(grids, callsign, band, args.continents)
    else:
        print("No Maidenhead grid squares found in file")

if __name__ == "__main__":
    main()
