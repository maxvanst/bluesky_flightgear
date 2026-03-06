## BlueSky FlightGear Flight Simulator plugin

This project is meant as an extension to 'BlueSky - The Open Air Traffic Simulator'. [https://github.com/TUDelft-CNS-ATM/bluesky] 
The Python BlueSky plugin creates a connection between BlueSky and the FlightGear Flight Simulator. [https://www.flightgear.org/]

<pre><img width="50" height="50" alt="FlightGear_Logo" src="https://github.com/user-attachments/assets/335b5adc-dbf1-4dc5-a0c5-01ebd5ee78b7" /></pre>

The following functionalities are madeby the plugin
- Transponder functionality, squawk, ident
- Ident by flashing FlightGear aircraft label inside BlueSky traffic
- BlueSky traffic can be visually seen in FlightGear using aircraft type and operator e.g. KLM B744 etc.
- TCAS TA/RA inside FlightGear with BlueSky traffic
- Sending instructions to FlightGear aircraft via CPDLC
- Retrieving FlightGear flightplan and inserting in BlueSky
- Slaving a FlightGear instance w.r.t. a BlueSky aircraft

## Prerequisites
- BlueSky v1.1.1 or later
- Python 3.12.3 or later
- FlightGear v2024.1.4 or later

## Installation
1) Navigate to the plugin folder inside your BlueSky installation
2) Download source code with <pre>git clone https://github.com/maxvanst/bluesky-flightgear.git</pre> or use the ZIP download
3) Place entire bluesky-flightgear directory inside the BlueSky plugin folder 
4) Add the following lines to settings.cfg inside your BlueSky installation:
<pre>
      flightgear_recv_interface = [YOUR_RECV_FLIGHTGEAR_INTERFACE]
      flightgear_recv_port = [YOUR_RECV_FLIGHTGEAR_PORT]
</pre>

## Running with FlightGear
1) Navigate to your FLIGHTGEAR_ROOT directory.
2) Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.
3) Start FlightGear
4) Within the main launcher window scroll down to additional settings of FlightGear and add the following items:
<pre>
   --generic=socket,out,1,[YOUR_RECV_FLIGHTGEAR_INTERFACE],[YOUR_BLUESKY_FLIGHTSIM_RECV_PORT],udp,bluesky 
   --multiplay=in,10,[YOUR_FLIGHTGEAR_MULTIPLAY_LISTEN_INTERFACE],[YOUR_FLIGHTGEAR_MULTIPLAY_IN_PORT]
   --prop:/bluesky/sim_name=[YOUR_FLIGHTGEAR_SIMNAME]
   --prop:/bluesky/sim_ip=[YOUR_FLIGHTGEAR_IP_ADDRESS]
   --prop:/bluesky/sim_traffic_recv_port=[YOUR_FLIGHTGEAR_TRAFFIC_RECV_PORT]
   --prop:/bluesky/telnet_port=[YOUR_FLIGHTGEAR_TELNET_PORT]
   --callsign=[YOUR_CALLSIGN]
   --disable-ai-traffic 
</pre>
5) Ensure [YOUR_BLUESKY_IP] and [YOUR_BLUESKY_FLIGHTSIM_RECV_PORT] are according to your BlueSky settings.cfg and network configuration
7) Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
8) Start the plugin: FLIGHTGEAR ON

## Command overview
- FLIGHTGEAR [ON/OFF]
- FGLIST
- FGSHOW [ON/OFF]
