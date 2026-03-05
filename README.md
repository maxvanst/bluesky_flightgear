## BlueSky Flight Simulator plugin

This project is meant as an extension to 'BlueSky - The Open Air Traffic Simulator'. [https://github.com/TUDelft-CNS-ATM/bluesky] 
The Python BlueSky plugin creates a connection between BlueSky and a Flight Simulator.
Currently two Flight Simulators are supported:
- The open source flight simulator FlightGear [https://www.flightgear.org/]
- The commercial flight simulator X-Plane. [https://www.x-plane.com/].

The following functionalities are madeby the plugin
- Transponder functionality, squawk, ident
- Ident by flashing FlightGear aircraft label inside BlueSky traffic
- BlueSky traffic can be visually seen in FlightGear using aircraft type and operator e.g. KLM B744 etc.
- TCAS TA/RA inside FlightGear with BlueSky traffic
- Sending instructions to FlightGear aircraft via CPDLC
- Retrieving FlightGear flightplan and inserting in BlueSky

## Prerequisites
- BlueSky v1.1.1 or later
- Python 3.12.3 or later
- FlightGear v2024.1.4 or later
- X-Plane 12.4.0 or later

<pre><img width="50" height="50" alt="FlightGear_Logo" src="https://github.com/user-attachments/assets/335b5adc-dbf1-4dc5-a0c5-01ebd5ee78b7" />    <img width="200" height="100" alt="image" src="https://github.com/user-attachments/assets/9af8b3e3-3f34-4d0c-8c66-0097d20ffd33" /></pre>

## Installation
1) Navigate to the plugin folder inside your BlueSky installation
2) Download source code with <pre>git clone https://github.com/maxvanst/bluesky-flightsim.git</pre> or use the ZIP download
3) Add the following lines to settings.cfg inside your BlueSky installation:
<pre>
   flightsim_recv_port = [YOUR_BLUESKY_FLIGHTSIM_RECV_PORT]
</pre>

## Running with FlightGear
1) Navigate to your FLIGHTGEAR_ROOT directory.
2) Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.
3) Start FlightGear
4) Within the main launcher window scroll down to additional settings of FlightGear and add the following items:
<pre>
   --generic=socket,out,1,[YOUR_BLUESKY_IP],[YOUR_BLUESKY_FLIGHTSIM_RECV_PORT],udp,bluesky 
   --multiplay=in,10,localhost,5000 
   --disable-ai-traffic 
   --callsign=[YOUR_CALLSIGN]
</pre>
5) Ensure [YOUR_BLUESKY_IP] and [YOUR_BLUESKY_FLIGHTSIM_RECV_PORT] are according to your BlueSky settings.cfg and network configuration
7) Start BlueSky: PLUGINS FLIGHTSIM should load the plugin
8) Start the plugin: FLIGHTSIM ON

## Running with X-Plane 12
1) Start X-Plane 12
2) Navigate to Settings/Data Output
3) Add the following indices to 'Network via UDP': 3, 18, 17, 20, 104
4) On the right side of the screen a Network Configuration widget is present. Add [YOUR_BLUESKY_IP] and [YOUR_BLUESKY_FLIGHTSIM_RECV_PORT].
5) Change Output Rate of UDP to 1.0 packet/sec
