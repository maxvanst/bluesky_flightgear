-- Simple FlightGear Multiplayer Wireshark dissector
-- Allows filter on the protocol 'fgmp' to see UDP packets using the FlightGear Multiplayer Protocol
--
-- For documentation see: https://wiki.flightgear.org/Multiplayer_protocol
-- and: https://www.wireshark.org/docs/wsug_html_chunked/ChPluginFolders.html

local fgmp = Proto("fgmp", "FlightGear Multiplayer")

-- Protocol fields
local f = fgmp.fields

f.magic       = ProtoField.string("fgmp.magic", "Magic")
f.version     = ProtoField.uint32("fgmp.version", "Protocol Version", base.HEX)
f.msgid       = ProtoField.uint32("fgmp.msgid", "Message ID", base.DEC)
f.msglen      = ProtoField.uint32("fgmp.msglen", "Message Length", base.DEC)
f.range       = ProtoField.float("fgmp.range", "Requested Range (nm)", base.DEC)
f.reply_port  = ProtoField.uint32("fgmp.reply_port", "Reply Port", base.DEC)
f.callsign    = ProtoField.string("fgmp.callsign", "Callsign")

-- Position message
f.model       = ProtoField.string("fgmp.model", "Aircraft Model")

f.time        = ProtoField.double("fgmp.time", "Time")
f.lag         = ProtoField.double("fgmp.lag", "Network Lag")

f.pos_x       = ProtoField.double("fgmp.pos.x", "Position X")
f.pos_y       = ProtoField.double("fgmp.pos.y", "Position Y")
f.pos_z       = ProtoField.double("fgmp.pos.z", "Position Z")

f.ori_x       = ProtoField.float("fgmp.orientation.x", "Orientation X")
f.ori_y       = ProtoField.float("fgmp.orientation.y", "Orientation Y")
f.ori_z       = ProtoField.float("fgmp.orientation.z", "Orientation Z")

f.vel_x       = ProtoField.float("fgmp.velocity.x", "Velocity X")
f.vel_y       = ProtoField.float("fgmp.velocity.y", "Velocity Y")
f.vel_z       = ProtoField.float("fgmp.velocity.z", "Velocity Z")

f.av_x        = ProtoField.float("fgmp.angular_velocity.x", "Angular Velocity X")
f.av_y        = ProtoField.float("fgmp.angular_velocity.y", "Angular Velocity Y")
f.av_z        = ProtoField.float("fgmp.angular_velocity.z", "Angular Velocity Z")

f.la_x        = ProtoField.float("fgmp.linear_accel.x", "Linear Acceleration X")
f.la_y        = ProtoField.float("fgmp.linear_accel.y", "Linear Acceleration Y")
f.la_z        = ProtoField.float("fgmp.linear_accel.z", "Linear Acceleration Z")
 
f.aa_x        = ProtoField.float("fgmp.angular_accel.x", "Angular Acceleration X")
f.aa_y        = ProtoField.float("fgmp.angular_accel.y", "Angular Acceleration Y")
f.aa_z        = ProtoField.float("fgmp.angular_accel.z", "Angular Acceleration Z")

f.properties = ProtoField.bytes("fgmp.properties", "Properties")

local MSG_POSITION = 7

function fgmp.dissector(buffer, pinfo, tree)

    -- Need at least the 32-byte header.
    if buffer:len() < 32 then
        return
    end

    -- FlightGear magic "FGFS"
    if buffer(0,4):string() ~= "FGFS" then
        return
    end

    pinfo.cols.protocol = "FGMP"

    local root = tree:add(fgmp, buffer(), "FlightGear Multiplayer")

    ------------------------------------------------------------
    -- Header
    ------------------------------------------------------------

    local header = root:add(buffer(0,32), "Multiplayer Header")

    header:add(f.magic, buffer(0,4))

    local version = buffer(4,4):uint()
    header:add(f.version, buffer(4,4))

    local msgid = buffer(8,4):uint()
    header:add(f.msgid, buffer(8,4))

    header:add(f.msglen, buffer(12,4))

    -- Requested visibility range is represented as an XDR float.
    header:add(f.range, buffer(16,4))

    header:add(f.reply_port, buffer(20,4))

    -- Callsign is an 8-byte zero-terminated field.
    local callsign = buffer(24,8):stringz()
    header:add(f.callsign, buffer(24,8))

    ------------------------------------------------------------
    -- Position message
    ------------------------------------------------------------

    if msgid ~= MSG_POSITION then
        return
    end

    if buffer:len() < 32 + 196 then
        return
    end

    local offset = 32

    local pos = root:add(
        buffer(offset),
        "Position / Motion Data"
    )

    ------------------------------------------------------------
    -- Aircraft model
    ------------------------------------------------------------

    pos:add(f.model, buffer(offset,96))
    offset = offset + 96

    ------------------------------------------------------------
    -- Time / lag
    ------------------------------------------------------------

    pos:add(f.time, buffer(offset,8))
    offset = offset + 8

    pos:add(f.lag, buffer(offset,8))
    offset = offset + 8

    ------------------------------------------------------------
    -- ECEF position
    ------------------------------------------------------------

    local position = pos:add(
        buffer(offset,24),
        "ECEF Position"
    )

    position:add(f.pos_x, buffer(offset,8))
    offset = offset + 8

    position:add(f.pos_y, buffer(offset,8))
    offset = offset + 8

    position:add(f.pos_z, buffer(offset,8))
    offset = offset + 8

    ------------------------------------------------------------
    -- Orientation
    ------------------------------------------------------------

    local orientation = pos:add(
        buffer(offset,12),
        "Orientation"
    )

    orientation:add(f.ori_x, buffer(offset,4))
    offset = offset + 4

    orientation:add(f.ori_y, buffer(offset,4))
    offset = offset + 4

    orientation:add(f.ori_z, buffer(offset,4))
    offset = offset + 4

    ------------------------------------------------------------
    -- Velocity
    ------------------------------------------------------------

    local velocity = pos:add(
        buffer(offset,12),
        "Velocity"
    )

    velocity:add(f.vel_x, buffer(offset,4))
    offset = offset + 4

    velocity:add(f.vel_y, buffer(offset,4))
    offset = offset + 4

    velocity:add(f.vel_z, buffer(offset,4))
    offset = offset + 4

    ------------------------------------------------------------
    -- Angular velocity
    ------------------------------------------------------------

    local angular_velocity = pos:add(
        buffer(offset,12),
        "Angular Velocity"
    )

    angular_velocity:add(f.av_x, buffer(offset,4))
    offset = offset + 4

    angular_velocity:add(f.av_y, buffer(offset,4))
    offset = offset + 4

    angular_velocity:add(f.av_z, buffer(offset,4))
    offset = offset + 4

    ------------------------------------------------------------
    -- Linear acceleration
    ------------------------------------------------------------

    local linear_accel = pos:add(
        buffer(offset,12),
        "Linear Acceleration"
    )

    linear_accel:add(f.la_x, buffer(offset,4))
    offset = offset + 4

    linear_accel:add(f.la_y, buffer(offset,4))
    offset = offset + 4

    linear_accel:add(f.la_z, buffer(offset,4))
    offset = offset + 4

    ------------------------------------------------------------
    -- Angular acceleration
    ------------------------------------------------------------

    local angular_accel = pos:add(
        buffer(offset,12),
        "Angular Acceleration"
    )

    angular_accel:add(f.aa_x, buffer(offset,4))
    offset = offset + 4

    angular_accel:add(f.aa_y, buffer(offset,4))
    offset = offset + 4

    angular_accel:add(f.aa_z, buffer(offset,4))
    offset = offset + 4

    ------------------------------------------------------------
    -- Remaining data = FlightGear property stream.
    --
    -- The property section uses the 2017.2+ compact encoding
    -- in modern FlightGear
    ------------------------------------------------------------

    if offset < buffer:len() then
        root:add(
            f.properties,
            buffer(offset),
            "Properties"
        )
    end

    ------------------------------------------------------------
    -- Info column
    ------------------------------------------------------------

    pinfo.cols.info = string.format(
        "Position: %s [%s]",
        callsign,
        buffer(32,96):stringz()
    )
end


----------------------------------------------------------------
-- Heuristic registration.
-- 
-- Wireshark will call the dissector for UDP packets
-- and the magic check above will accept only FGFS packets.
----------------------------------------------------------------

local udp_table = DissectorTable.get("udp.port")

fgmp:register_heuristic("udp", function(buffer, pinfo, tree)
    if buffer:len() >= 4 and buffer(0,4):string() == "FGFS" then
        fgmp.dissector(buffer, pinfo, tree)
        return true
    end

    return false
end)
