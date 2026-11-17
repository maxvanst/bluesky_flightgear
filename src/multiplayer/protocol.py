# src/multiplayer/protocol.py

import struct

MAGIC = 0x46474653              # "FGFS"
PROTOCOL_VERSION = 0x00010001   # "1.1"
POSITION_DATA_ID = 0x00000007   # "7"
HEADER_SIZE = 32  

class FlightGearMultiplayerPacket:
    """
    The XDR encoded FlightGear Multiplayer Packet.
    As defined on https://wiki.flightgear.org/Multiplayer_protocol  
    The class contains the function to self-decode and self-encode using @classmethod
    """
    def __init__(self, magic: bytes, version: bytes, msg_id: int, msg_len: int, 
        req_range_nm: float, reply_port: int, callsign: str, 
        model_name: str, time: float, lag: float, position: tuple, 
        orientation: tuple, velocity: tuple, angular_velocity: tuple, 
        linear_acceleration: tuple, angular_acceleration: tuple):

        """
        |----------------------------------------------------------------------------------------------------------------------------------------------|
        | From: https://wiki.flightgear.org/Multiplayer_protocol                                                                                       |
        |--------------------|----------|--------------------------------------------------------------------------------------------------------------|                                                                                                                                             |
        | Field              | Size     | Remarks                                                                                                      |
        |--------------------|----------|--------------------------------------------------------------------------------------------------------------|
        | Magic              | 4 bytes  | Always 0x46474653 ("FGFS")                                                                                   |
        | Version            | 4 bytes  | Protocol version, currently 0x00010001 (1.1)                                                                 |
        | MsgId              | 4 bytes  | Defines what data is appended to the header. Can be 0x00000001 for chat messages (deprecated) or             |
        |                    |          | 0x00000007 for position data - all other values are outdated and ignored.                                    |
        | MsgLen             | 4 bytes  | Length of the data. Caution: This is not in bytes, see the description of the STRING data type.              |
        | RequestedRangeNm   | 4 bytes  | Requested visibility range in nm. The MP server can provide mp packets from any players within this          |
        |                    |          | range; but never over it.                                                                                    |
        | ReplyPort          | 4 bytes  | Deprecated and ignored                                                                                       |
        | Callsign           | 8 bytes  | Zero terminated array of characters representing the user callsign in text format                            |
        |--------------------|----------|--------------------------------------------------------------------------------------------------------------|
        """
        self.magic = magic
        self.version = version
        self.msg_id = msg_id
        self.msg_len = msg_len
        self.req_range_nm = req_range_nm
        self.reply_port = reply_port
        self.callsign = callsign
        
        """
        |----------------------------------------------------------------------------------------|
        | From: https://wiki.flightgear.org/Multiplayer_protocol                                 |
        |-----------|------------|---------------------------------------------------------------|
        | Field     | Size       | Remarks                                                       |
        | ModelName | 96 bytes   | Zero-terminated array of characters representing the aircraft |
        |           |            | model (/sim/model/path) used by the user                      |
        | time      | 8 bytes    | Time when this message was generated (double)                 |
        | lag       | 8 bytes    | Time offset for network lag (double)                          |
        | PosX      | 8 bytes    | XDR-encoded double; X-coordinate of user's position           |
        | PosY      | 8 bytes    | XDR-encoded double; Y-coordinate of user's position           |
        | PosZ      | 8 bytes    | XDR-encoded double; Z-coordinate of user's position           |
        | OriX      | 4 bytes    | XDR-encoded float; X-orientation of the user                  |
        | OriY      | 4 bytes    | XDR-encoded float; Y-orientation of the user                  |
        | OriZ      | 4 bytes    | XDR-encoded float; Z-orientation of the user                  |
        | VelX      | 4 bytes    | XDR-encoded float; velocity in X direction                    |
        | VelY      | 4 bytes    | XDR-encoded float; velocity in Y direction                    |
        | VelZ      | 4 bytes    | XDR-encoded float; velocity in Z direction                    |
        | AV1       | 4 bytes    | XDR-encoded float; 1st component of angular velocity vector   |
        | AV2       | 4 bytes    | XDR-encoded float; 2nd component of angular velocity vector   |
        | AV3       | 4 bytes    | XDR-encoded float; 3rd component of angular velocity vector   |
        | LA1       | 4 bytes    | XDR-encoded float; 1st component of linear acceleration       |
        | LA2       | 4 bytes    | XDR-encoded float; 2nd component of linear acceleration       |
        | LA3       | 4 bytes    | XDR-encoded float; 3rd component of linear acceleration       |    
        | AA1       | 4 bytes    | XDR-encoded float; 1st component of angular acceleration      |
        | AA2       | 4 bytes    | XDR-encoded float; 2nd component of angular acceleration      |
        | AA3       | 4 bytes    | XDR-encoded float; 3rd component of angular acceleration      |
        | pad       | Up to 8    | Padding to make the data size a multiple of 8 bytes           |
        |-----------|------------|---------------------------------------------------------------|
        """
        self.model_name = model_name
        self.time = time
        self.lag = lag
        self.position = position
        self.orientation = orientation
        self.velocity = velocity
        self.angular_velocity = angular_velocity
        self.linear_acceleration = linear_acceleration
        self.angular_accelleration = angular_acceleration

    def encode(self) -> bytes:
        header = struct.pack('!6I8s', self.magic, self.version, self.msg_id, self.msg_len, self.req_range_nm, self.reply_port, self.callsign) # '!6I8s' enforces max length of 32 bytes
        payload = struct.pack(self.model_name, self.time, self.lag, self.position, self.orientation, self.velocity, self.angular_accelleration, self.linear_acceleration, self.angular_accelleration)
        return header + payload

    @classmethod
    def decode(cls, packet: bytes) -> "FlightGearMultiplayerPacket":
        offset = 0 
        magic = packet[offset:offset+4]
        offset += 4
        version = packet[offset:offset+4]
        offset += 4
        msg_id = struct.unpack_from(">I", packet, offset)[0] # struct.unpack_from returns tuple, therefore select 0 index.
        offset += 4
        msg_len = struct.unpack_from(">I", packet, offset)[0]
        offset += 4
        req_range_nm = struct.unpack_from(">f", packet, offset)[0]
        offset += 4
        reply_port = struct.unpack_from(">I", packet, offset)[0]
        offset += 4
        callsign = packet[offset:offset+8].split(b"\0", 1)[0].decode("utf-8", errors="replace")
        offset += 8
        model_name = packet[offset:offset+96].split(b"\0", 1)[0].decode("utf-8", errors="replace")
        offset += 96
        time = struct.unpack_from(">d", packet, offset)[0]
        offset += 8
        lag = struct.unpack_from(">d", packet, offset)[0]
        offset += 8
        position = struct.unpack_from(">ddd", packet, offset)
        offset += 24
        orientation = struct.unpack_from(">fff", packet, offset)
        offset += 12
        velocity = struct.unpack_from(">fff", packet, offset)
        offset += 12
        angular_velocity = struct.unpack_from(">fff", packet, offset)
        offset += 12
        linear_acceleration = struct.unpack_from(">fff", packet, offset)
        offset += 12
        angular_acceleration = struct.unpack_from(">fff", packet, offset)
        offset += 12

        return cls(
            magic = magic,
            version = version,
            msg_id = msg_id,
            msg_len = msg_len,
            req_range_nm = req_range_nm,
            reply_port = reply_port,
            callsign = callsign,
            model_name = model_name, 
            time = time, 
            lag = lag, 
            position = position, 
            orientation = orientation, 
            velocity = velocity, 
            angular_velocity = angular_velocity, 
            linear_acceleration = linear_acceleration, 
            angular_acceleration = angular_acceleration)