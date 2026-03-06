def model_mapping(actype: str, operator="main"):
    """
    Map BlueSky actype => FlightGear Aircraft Model
    """
    # -------------------- Boeing --------------------- #
    # Boeing 787
    if actype == "B789":
        model = f"AI/Aircraft/787/789-{operator}.xml"
    elif actype == "B788":
        model = f"AI/Aircraft/787/788-{operator}.xml"
    # Boeing 777
    elif actype == "B77F":
        model = f"AI/Aircraft/777/77F-{operator}.xml"
    elif actype == "B77L":
        model = f"AI/Aircraft/777/77L-{operator}.xml"
    elif actype == "B77W":
        model = f"AI/Aircraft/777/77W-{operator}.xml"
    # Boeing 767
    elif actype == "B76W":
        model = f"AI/Aircraft/767/76W-{operator}.xml"
    elif actype == "B76Y":
        model = f"AI/Aircraft/767/76Y-{operator}.xml"
    elif actype == "B767":
        model = f"AI/Aircraft/767/767-{operator}.xml"
    elif actype == "B76W":
        model = f"AI/Aircraft/767/76W-{operator}.xml"
    # Boeing 757
    elif actype == "B752":
        model = f"AI/Aircraft/757/757-200-{operator}.xml"
    elif actype == "B753":
        model = f"AI/Aircraft/757/757-300-{operator}.xml"
    # Boeing 747
    elif actype == "B744":
        model = f"AI/Aircraft/747/744-{operator}.xml"
    elif actype == "B74N":
        model = f"AI/Aircraft/747/74N-{operator}.xml"
    elif actype == "B74Y":
        model = f"AI/Aircraft/747/74Y-{operator}.xml"
    elif actype == "B74F":
        model = f"AI/Aircraft/747/74F-{operator}.xml"
    # Boeing 737
    elif actype == "B739":
        model = f"AI/Aircraft/737/73J-{operator}.xml"
    elif actype == "B738":
        model = f"AI/Aircraft/737/738-{operator}.xml"
    # -------------------- Airbus --------------------- #
    # Airbus A380
    elif actype == "A388":
        model = f"AI/Aircraft/A380/388-{operator}.xml"
    # Airbus A350
    elif actype == "A359":
        model = f"AI/Aircraft/A350/359-{operator}.xml"
    # Airbus A340    
    elif actype == "A346":
        model = f"AI/Aircraft/A346/A346-{operator}.xml"
    elif actype == "A345":
        model = f"AI/Aircraft/A345/A345-{operator}.xml"
    elif actype == "A343":
        model = f"AI/Aircraft/A343/A343-{operator}.xml"
    elif actype == "A342":
        model = f"AI/Aircraft/A342/A342-{operator}.xml"
    # Airbus A330
    elif actype == "A333":
        model = f"AI/Aircraft/A333/A333-{operator}.xml"
    elif actype == "A332":
        model = f"AI/Aircraft/A332/A332-{operator}.xml"
    elif actype == "A330MRTT":
        model = f"AI/Aircraft/A330/A330-MRTT.xml"
    # Airbus A321
    elif actype == "A321":
        model = f"AI/Aircraft/A321/A321-{operator}.xml"
    # Airbus A320
    elif actype == "A320":
        model = f"AI/Aircraft/A320/A320-{operator}.xml"
    # Airbus A319
    elif actype == "A319":
        model = f"AI/Aircraft/A319/A319-{operator}.xml"
    # ----------------- Cessna -------------------- #
    # Cessna 172
    elif actype == "C172":
        model = f"AI/Aircraft/c172/c-fgfs.xml"
    else:
        print(f"[FLIGHTGEAR]: {actype} not found in AI/models in FlightGear - using B744 as default model")
        model = f"AI/Aircraft/747/744-{operator}.xml"

    return model