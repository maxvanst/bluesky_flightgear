## Installation
- Place the BlueSky Flightgear plugin inside ./plugin directory inside BlueSky installation
- Place ./protocol/bluesky.xml inside $FLIGHTGEAR_ROOT/Protocol/ 

## Running 
- Start FlightGear Linux: ./flightgear-2024.1.4-linux-amd64.AppImage --launcher 
- Additional settings of FlightGear --generic=socket,out,1,localhost,5501,udp,bluesky --disable-ai-traffic
- Add: "flightgear_host = "127.0.0.1" flightgear_port = 5501" to settings.cfg, according to own setup:
    *flightgear_host = '127.0.0.1'
    *flightgear_port = 5501
- Ensure address and port of FlightGear are properly set in settings.cfg inside BlueSky if not using localhost
- Start BlueSky: PLUGINS FLIGHTGEAR should load the plugin
- Start the plugin: FLIGHTGEAR ON

## Functionality
- FlightGear aircraft visible inside BlueSky
- FlightGear IDENT results in IDENT inside BlueSky
- FlightGear Flightplan ORIGIN and DESTINATION updated inside BlueSky

## Docs
For additional info:
- https://wiki.flightgear.org/
- https://wiki.flightgear.org/Command_line_options
- https://wiki.flightgear.org/Aircraft_properties_reference
- https://wiki.flightgear.org/Flightplan_XML_formats