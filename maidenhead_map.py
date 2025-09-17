#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from collections import Counter, defaultdict

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

def parse_cabrillo_by_band(filename):
    """Extract Maidenhead grid squares by band and callsign from Cabrillo format file"""
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
                        freq = parts[1]  # Frequency in kHz
                        band = freq_to_band(freq)
                        
                        for part in parts:
                            part = part.upper()
                            if (len(part) == 4 and 
                                part[0] in 'ABCDEFGHIJKLMNOPQR' and 
                                part[1] in 'ABCDEFGHIJKLMNOPQR' and 
                                part[2] in '0123456789' and 
                                part[3] in '0123456789'):
                                grids_by_band[band].append(part)
                            elif (len(part) == 6 and 
                                  part[0] in 'ABCDEFGHIJKLMNOPQR' and 
                                  part[1] in 'ABCDEFGHIJKLMNOPQR' and 
                                  part[2] in '0123456789' and 
                                  part[3] in '0123456789' and
                                  part[4] in 'ABCDEFGHIJKLMNOPQRSTUVWX' and
                                  part[5] in 'ABCDEFGHIJKLMNOPQRSTUVWX'):
                                grids_by_band[band].append(part)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}, callsign
    
    return dict(grids_by_band), callsign

def freq_to_band(freq_str):
    """Convert frequency string to band name"""
    freq = int(freq_str)
    if freq == 50:
        return "6m"
    elif freq == 144:
        return "2m"
    elif freq == 222:
        return "1.25m"
    elif freq == 432:
        return "70cm"
    elif freq == 902 or freq == 903:
        return "33cm"
    elif freq == 1296:
        return "23cm"
    else:
        return f"{freq}MHz"

def create_grid_map(grids, callsign, band, output_file):
    """Create color-coded map of Maidenhead grid squares for a specific band"""
    
    grid_counts = Counter(grids)
    
    # Filter for Americas region
    valid_grids = {}
    for grid, count in grid_counts.items():
        bounds = maidenhead_to_bounds(grid)
        if bounds:
            lat_min, lat_max, lon_min, lon_max = bounds
            if -180 <= lon_min <= -30 and -60 <= lat_min <= 80:
                valid_grids[grid] = count
    
    if not valid_grids:
        print(f"No valid grid squares found for {band}")
        return
    
    fig = plt.figure(figsize=(14, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-180, -30, -60, 80], crs=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.LAND, alpha=0.2, color='lightgray')
    ax.add_feature(cfeature.OCEAN, alpha=0.2, color='lightblue')
    
    # Plot grid squares as rectangles
    max_count = max(valid_grids.values())
    for grid, count in valid_grids.items():
        bounds = maidenhead_to_bounds(grid)
        if bounds:
            lat_min, lat_max, lon_min, lon_max = bounds
            
            intensity = count / max_count
            color = plt.cm.Reds(0.3 + 0.7 * intensity)
            
            rect = patches.Rectangle((lon_min, lat_min), 
                                   lon_max - lon_min, 
                                   lat_max - lat_min,
                                   linewidth=0.5, 
                                   edgecolor='black', 
                                   facecolor=color,
                                   alpha=0.8,
                                   transform=ccrs.PlateCarree())
            ax.add_patch(rect)
    
    # Add grid field labels
    field_centers = {}
    for grid in valid_grids.keys():
        field = grid[:2]
        if field not in field_centers:
            lon_center = (ord(field[0]) - ord('A')) * 20 - 180 + 10
            lat_center = (ord(field[1]) - ord('A')) * 10 - 90 + 5
            field_centers[field] = (lon_center, lat_center)
    
    for field, (lon, lat) in field_centers.items():
        ax.text(lon, lat, field, fontsize=12, fontweight='bold',
                ha='center', va='center', color='blue',
                transform=ccrs.PlateCarree())
    
    ax.gridlines(draw_labels=True, alpha=0.3)
    
    plt.title(f'{callsign} - {band} Band - Maidenhead Grid Squares\nRadio Contest Contacts - North & South America', 
              fontsize=14, fontweight='bold')
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, 
                               norm=plt.Normalize(vmin=1, vmax=max_count))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6)
    cbar.set_label('Number of Contacts', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Map saved as {output_file}")
    print(f"{band}: {len(valid_grids)} unique grid squares, {sum(valid_grids.values())} contacts")

def main():
    """Main entry point for console script"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: maidenhead-map <cabrillo_file>")
        print("   or: python maidenhead_map.py <cabrillo_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    grids_by_band, callsign = parse_cabrillo_by_band(filename)
    
    if grids_by_band:
        for band, grids in grids_by_band.items():
            output_file = f"{callsign}_{band}_maidenhead_map.png"
            create_grid_map(grids, callsign, band, output_file)
    else:
        print("No Maidenhead grid squares found in Cabrillo file")

if __name__ == "__main__":
    main()
