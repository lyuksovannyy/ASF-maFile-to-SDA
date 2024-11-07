# ASF-maFile-to-SDA
Easily convert most of ASF's .maFiles to SDA

## Dependencies
- Python 3.11

## Usage
`python main.py`
full path example: C:\ArchiSteamFarm\

## Additional info
- Weak .maFiles cannot be converted (that contain only **shared_secret** and **identity_secret**)
- .maFiles without generated "Session" in it, must be manually imported into SDA (you can identify them by non standard name format (SDA's standard format: 1234567890.maFile))
