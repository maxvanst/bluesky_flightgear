# BlueSky FlightGear plugin

This project is an extension plugin to <b>'BlueSky - The Open Air Traffic Simulator'</b>. The plugin creates a connection between BlueSky and the FlightGear Flight Simulator. The project creates a multi-pilot platform to enable synced scenario and traffic generation for human-in-the-loop experiments. 

<b>'Citation info:</b> M.J. van Stuijvenberg, "<i>BlueSky FlightGear Plugin</i>"

## Features
- Multi-instance support (multiple concurrent FlightGear clients on LAN can connect, each pilot seeing all other pilots and all BlueSky traffic)

## Prerequisites
- Python >= 3.14.4 [https://www.python.org/]
- BlueSky >= v1.1.1 [https://github.com/TUDelft-CNS-ATM/bluesky]
- FlightGear >= v2024.1.4 [https://www.flightgear.org/]

## Installation
1) Navigate to the plugin folder inside your BlueSky installation
2) Download source code:
   
   ```sh
   git clone https://github.com/maxvanst/bluesky-flightgear.git
   ```
   or use the ZIP download
3) Make sure bluesky_flightgear directory is inside the BlueSky plugin folder 
4) Add the following network details in settings.cfg of BlueSky on how to receive from and send to FlightGear:
   ```sh
   flightgear_recv_interface = 'localhost'
   flightgear_recv_port = '5000'
   ```

## Running with FlightGear
1) Start FlightGear
2) Within the main launcher window scroll down to additional settings of FlightGear and add the following items:
   ```sh
      --multiplay=out,10,localhost,5000 
      --multiplay=in,10,localhost,5001
      --callsign=PHLAB
      --airport=EHRD
      --disable-ai-traffic 
   ```
3) Make sure the networking interfaces and ports match the BlueSky server's settings.cfg.
4) Start BlueSky: ``` PLUGINS FLIGHTGEAR ``` should load the plugin
5) Start the plugin: ``` FLIGHTGEAR ON ```

## BlueSky command overview
```sh
   FLIGHTGEAR [ON/OFF] # Start or Stop the plugin
   FLIGHTGEAR HELP     # Receive all possible commands
```

## Tools
### Debug
Place the [launch.json](tools/debug/launch.json) inside .vscode to allow BlueSky plugin debug.

### Wireshark
Place the [flightgear.lua](tools/wireshark/flightgear.lua) inside the plugin folder of Wireshark. This allows easier identification and filtering of the FlightGear Multiplayer Protocol

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Links:
- BlueSky: [https://github.com/TUDelft-CNS-ATM/bluesky]
- FlightGear: [https://www.flightgear.org/]