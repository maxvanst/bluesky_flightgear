## Installation
- place bluesky.xml inside $FLIGHTGEAR_ROOT/Protocol/ 
- ensure address and port are properly set in settings.cfg inside BlueSky

## Running 
- Start FlightGear ./flightgear-2024.1.4-linux-amd64.AppImage --launcher 
- Add flightgear .py folder to plugins folder in BlueSky
- Additional settings of FlightGear --generic=socket,out,1,localhost,5501,udp,bluesky --disable-ai-traffic
- Add: "flightgear_host = "127.0.0.1" flightgear_port = 5501" to settings.cfg, according to own setup

## Docs
- https://wiki.flightgear.org/
- https://wiki.flightgear.org/Command_line_options
- https://wiki.flightgear.org/Aircraft_properties_reference