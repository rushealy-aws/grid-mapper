# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
