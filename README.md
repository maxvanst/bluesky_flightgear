## Prerequisites
- Python 3.12.3
- FlightGear v2024.1.4
- BlueSky v1.1.1 or later

## Installation
In order to install the BlueSky FlightGear Plugin:
- Place the BlueSky Flightgear plugin inside the ./plugin directory within your BlueSky installation
- Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.

## Running 
- Start FlightGear, For Linux: ./flightgear-2024.1.4-linux-amd64.AppImage --launcher 
- Additional settings of FlightGear --generic=socket,out,1,localhost,5501,udp,bluesky --telnet=5502 --callsign=PHLAB
- Ensure address and port of FlightGear are properly set in settings.cfg inside BlueSky if not using localhost
- Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
- Start the plugin: FLIGHTGEAR ON

## Docs
For additional information:
- https://wiki.flightgear.org/
- https://wiki.flightgear.org/Command_line_options
- https://wiki.flightgear.org/Aircraft_properties_reference
- https://wiki.flightgear.org/Multiplayer_protocol
- https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py