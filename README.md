## BlueSky FlightGear plugin
This Python plugin is meant as an extension to the 'BlueSky - The Open Air Traffic Simulator'. [https://github.com/TUDelft-CNS-ATM/bluesky]
The plugin creates a connection between BlueSky and the popular open source flight simulator FlightGear [https://www.flightgear.org/]. 
This includes showing the FlightGear simulated aircraft in BlueSky and sending BlueSky traffic to FlightGear.
The following items are supported:
- Transponder functionality, squawk, ident
- Ident by flashing FlightGear aircraft label inside BlueSky traffic
- BlueSky traffic can be visually seen in FlightGear using aircraft type and operator e.g. KLM B744 etc.
- TCAS TA/RA inside FlightGear with BlueSky traffic
- Sending instructions to FlightGear aircraft via CPDLC
- Retrieving FlightGear flightplan and inserting in BlueSky

## Prerequisites
- Python 3.12.3 or later
- FlightGear v2024.1.4
- BlueSky v1.1.1 or later

## Installation
In order to install the BlueSky FlightGear Plugin:
- Place the BlueSky Flightgear plugin inside the ./plugin directory within your BlueSky installation
- Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.

## Running 
- Start FlightGear
- Within the main launcher window scroll down to: additional settings of FlightGear.
- Add the following items:
   * --generic=socket,out,1,localhost,5000,udp,bluesky 
   * --multiplay=out,10,localhost,5001 
   * --multiplay=in,10,localhost,5002 
   * --telnet=socket,bi,60,localhost,5003,tcp 
   * --disable-ai-traffic 
   * --prop:/bluesky/client/name=[YOUR_CLIENT_NAME]
   * --callsign=PHLAB
   * 
- Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
- Start the plugin: FLIGHTGEAR ON
- Start the BlueSky simulation by pressing 'Op'

## Docs
For additional information:
- https://wiki.flightgear.org/
- https://wiki.flightgear.org/Command_line_options
- https://wiki.flightgear.org/Aircraft_properties_reference
- https://wiki.flightgear.org/Multiplayer_protocol
- https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py
