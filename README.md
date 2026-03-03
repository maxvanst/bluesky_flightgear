## BlueSky FlightSim plugin

This Python application is meant as an extension to 'BlueSky - The Open Air Traffic Simulator'. [https://github.com/TUDelft-CNS-ATM/bluesky] The application creates a connection between BlueSky and the popular open source flight simulator FlightGear [https://www.flightgear.org/] and the popular closed sourced commercial flight simulator X-Plane. [https://www.x-plane.com/].

The following functionalities are present
- Transponder functionality, squawk, ident
- Ident by flashing FlightGear aircraft label inside BlueSky traffic
- BlueSky traffic can be visually seen in FlightGear using aircraft type and operator e.g. KLM B744 etc.
- TCAS TA/RA inside FlightGear with BlueSky traffic
- Sending instructions to FlightGear aircraft via CPDLC
- Retrieving FlightGear flightplan and inserting in BlueSky

## Prerequisites
- BlueSky v1.1.1 or later
- Python 3.12.3 or later
- FlightGear v2024.1.4
- X-Plane 12

<pre><img width="50" height="50" alt="FlightGear_Logo" src="https://github.com/user-attachments/assets/335b5adc-dbf1-4dc5-a0c5-01ebd5ee78b7" />    <img width="200" height="100" alt="image" src="https://github.com/user-attachments/assets/9af8b3e3-3f34-4d0c-8c66-0097d20ffd33" />
</pre>

In order to install the BlueSky FlightGear Plugin:
- Place the BlueSky Flightgear plugin inside the ./plugin directory within your BlueSky installation
- Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.

## Running with FlightGear
- Start FlightGear
- Within the main launcher window scroll down to: additional settings of FlightGear.
- Add the following items:
<pre>
   --generic=socket,out,1,localhost,5000,udp,bluesky 
   --multiplay=out,10,localhost,5001 
   --multiplay=in,10,localhost,5002 
   --telnet=socket,bi,60,localhost,5003,tcp 
   --disable-ai-traffic 
   --prop:/bluesky/client/name=[YOUR_FLIGHTGEAR_CLIENT_NAME]
   --prop:/bluesky/client/address=[YOUR_FLIGHTGEAR_CLIENT_ADDRESS]
   --callsign=[YOUR_CALLSIGN]
</pre>
     
- Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
- Start the plugin: FLIGHTGEAR ON
- Start the BlueSky simulation by pressing 'Op'

## Running with X-Plane 12
-
