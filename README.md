# BlueSky FlightGear plugin 
This project is meant as an extension to <b>'BlueSky - The Open Air Traffic Simulator'</b>.
The plugin creates a connection between BlueSky and the FlightGear Flight Simulator.
This connection is made using a custom UDP BlueSky protocol using the generic protocol from FlightGear.
BlueSky traffic is injected using the FlightGear Multiplayer Protocol.
Additionally, simulation parameters that do not require a constant UDP socket are changed using a Telnet connection made by the flightgear-python package by <i>Julianne Swinoga</i>.
The FlightGear Multiplayer traffic protocol in Python was written with inspiration from <i>zayamatias</i> implementation which he shared on the FlightGear forum (see links).

<pre><img width="50" height="50" alt="FlightGear_Logo" src="https://github.com/user-attachments/assets/335b5adc-dbf1-4dc5-a0c5-01ebd5ee78b7" /></pre>
<img width="3431" height="1345" alt="image" src="https://github.com/user-attachments/assets/0717db1b-722b-470c-ab02-f3b626d4b1be" />

## Functionalities of the plugin:
- Transponder functionality, squawk, ident.
- Ident by flashing FlightGear aircraft label inside BlueSky traffic.
- BlueSky traffic can be visually seen in FlightGear using FlightGear Multiplayer Protocol.
- TCAS TA/RA inside FlightGear reacting to BlueSky traffic.
- Sending instructions to FlightGear aircraft using an ATC voice inside FlightGear.
- Sending instructions to FlightGear aircraft via CPDLC.
- Retrieving FlightGear flightplan and inserting in BlueSky.
- Changing FlightGear sim time using BlueSky commands.
- FlightGear simulator follows sim state of BlueSky [PAUSE]




https://github.com/user-attachments/assets/0143ce12-a7cf-4dea-9214-58ebd9c2e65e



## Prerequisites
- BlueSky v1.1.1 or later [https://github.com/TUDelft-CNS-ATM/bluesky]
- Python 3.12.3 or later [https://www.python.org/]
- FlightGear v2024.1.4 or later [https://www.flightgear.org/]
- flightgear-python by Julianne Swinoga [https://github.com/julianneswinoga/flightgear-python/]

   ```sh
   pip install flightgear-python
   ```

## Installation
1) Navigate to the plugin folder inside your BlueSky installation
2) Download source code:
   
   ```sh
   git clone https://github.com/maxvanst/bluesky-flightgear.git
   ```
   or use the ZIP download
4) Place entire bluesky-flightgear directory inside the BlueSky plugin folder 
5) Add the following lines to settings.cfg inside your BlueSky installation:

```sh
      flightgear_recv_interface = [RECV_FLIGHTGEAR_INTERFACE]
      flightgear_recv_port = [RECV_FLIGHTGEAR_PORT]
```

## Running with FlightGear
1) Navigate to your FLIGHTGEAR_ROOT directory.
2) Place ./protocol/bluesky.xml inside the $FLIGHTGEAR_ROOT/Protocol/ directory.
3) Start FlightGear
4) Within the main launcher window scroll down to additional settings of FlightGear and add the following items:
```sh
   --generic=socket,out,10,[RECV_FLIGHTGEAR_INTERFACE],[RECV_FLIGHTGEAR_PORT],udp,bluesky
   --multiplay=out,10,[TFC_OUT_INTERFACE],[TFC_OUT_PORT]
   --multiplay=in,10,[TFC_RECV_INTERFACE],[TFC_RECV_PORT]
   --telnet=socket,bi,60,[TELNET_RECV_INTERFACE],[TELNET_RECV_PORT],tcp
   --prop:/bluesky/sim_name=[SIM_NAME]
   --prop:/bluesky/sim_ip=[SIM_IP_ADDRESS]
   --prop:/bluesky/sim_traffic_recv_port=[TFC_RECV_PORT]
   --prop:/bluesky/telnet_port=[TELNET_RECV_PORT]
   --callsign=[CALLSIGN]
   --prop:/aircraft/icao/type=[ICAO ACTYPE]
   --disable-ai-traffic 
```
Example when running on localhost interface:
```sh
   --generic=socket,out,10,localhost,5500,udp,bluesky
   --multiplay=out,10,localhost,5501 
   --multiplay=in,10,localhost,5502
   --telnet=socket,bi,60,localhost,5503,tcp
   --prop:/bluesky/sim_name=FG_SIM_1
   --prop:/bluesky/sim_ip=127.0.0.1
   --prop:/bluesky/sim_traffic_recv_port=5502
   --prop:/bluesky/telnet_port=5503
   --callsign=PHLAB
   --prop:/aircraft/icao/type=C550
   --disable-ai-traffic 
```

5) Ensure [RECV_FLIGHTGEAR_INTERFACE] and [RECV_FLIGHTGEAR_PORT] are according to your BlueSky settings.cfg and network configuration
7) Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
8) Start the plugin: FLIGHTGEAR ON

## BlueSky command overview
```sh
   FLIGHTGEAR [ON/OFF]
   FLIGHTGEAR_SETTIME CALLSIGN 18:00:00
   FLIGHTGEAR_GETHOST CALLSIGN
   FLIGHTGEAR_SENDCPDLC CALLSIGN "Your message inside here"
   FLIGHTGEAR_SENDATC CALLSIGN "Your message inside here"
   FLIGHTGEAR_VERSION
```

## Links:
- BlueSky: [https://github.com/TUDelft-CNS-ATM/bluesky]
- FlightGear: [https://www.flightgear.org/]
- flightgear-python package [https://github.com/julianneswinoga/flightgear-python/]
- zayamatias [https://github.com/zayamatias/FGRandomMultiplayer/blob/main/mp.py] 

## License
Distributed under the MIT License. See `LICENSE` for more information.
