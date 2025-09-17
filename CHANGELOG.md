# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-17

### Added
- Comprehensive amateur radio band support from 630m to 1mm (241 GHz)
- Full HF band support: 630m, 160m, 80m, 60m, 40m, 30m, 20m, 17m, 15m, 12m, 10m
- Extended VHF/UHF support: 6m, 2m, 1.25m, 70cm, 33cm, 23cm
- Microwave band support: 13cm, 9cm, 6cm, 3cm, 1.25cm, 6mm, 4mm, 2.5mm, 2mm, 1mm
- Cabrillo standard nomenclature compliance
- Support for both frequency ranges and common discrete frequencies
- Direct band name string parsing (e.g., "6M", "70CM", "23CM")

### Enhanced
- Improved frequency parsing with multiple format support
- Better handling of contest log frequency formats
- More accurate band identification for all amateur radio allocations

## [1.1.0] - 2025-09-17

### Added
- CSV file format support with automatic column detection
- Automatic file format detection based on file extension (.csv, .cbr, .log)
- Continent selection functionality with --continents argument
- Automatic continent detection based on grid squares in log
- Support for 6 continents: north_america, south_america, europe, africa, asia, oceania
- Dynamic map bounds based on selected continents
- Grid square filtering by continent
- Example CSV file for testing
- Command-line argument parsing with argparse

### Changed
- Map bounds now automatically adjust to selected continents instead of fixed Americas view
- Output filenames now include continent information
- Grid field labels only show for visible map areas
- Improved error handling and user feedback

### Enhanced
- Better CSV parsing with flexible column name detection
- More accurate continent boundary definitions
- Optimized map rendering for different geographic regions

## [1.0.0] - 2025-09-17

### Added
- Initial release of Maidenhead Contest Map Generator
- Support for Cabrillo format contest log parsing
- Multi-band analysis with separate maps per frequency band
- Accurate grid square boundary rendering (2° × 1° and 5' × 2.5')
- Grid field labels (EM, EN, EL, etc.) displayed on maps
- Color-coded contact density visualization
- Support for 6m, 2m, 1.25m, 70cm, 33cm, and 23cm bands
- Americas region coverage optimization
- High-resolution PNG output with callsign and band in filename
- MIT License
- Comprehensive documentation and examples

### Features
- Parses standard Cabrillo contest logs
- Creates separate maps for each frequency band found
- Shows actual geographic grid square boundaries
- Color intensity indicates contact density per grid
- Includes coastlines, borders, and geographic features
- Automatic callsign extraction from log headers
