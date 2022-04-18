#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import copy
import hashlib
import json
import os
import math
import serial
import socket
import struct
import sys
import threading
import time

debugEnabled, verboseEnabled = False, False
textMutex = threading.Lock()

def debug(text):
    global debugEnabled
    global textMutex

    if debugEnabled:
        textMutex.acquire()
        sys.stderr.write('[{:.6f}] {:s}\r\n'.format(time.time(), text))
        sys.stderr.flush()
        textMutex.release()

def verbose(text):
    global verboseEnabled
    global textMutex

    if verboseEnabled:
        textMutex.acquire()
        sys.stderr.write('[{:.6f}] {:s}\r\n'.format(time.time(), text))
        sys.stderr.flush()
        textMutex.release()

def listen(ident, fields, fn=None):
    try:
        match = fields['id'] in ident
    except:
        match = fields['id'] == ident

    if match:
        if fn is not None:
            return fn(fields)
        else:
            return True
    return False


class SerialStream:
    def __init__(self, dev, rate):
        self.socket = serial.Serial()
        self.socket.port     = dev
        self.socket.baudrate = rate
        self.socket.parity   = 'N'
        self.socket.rtscts   = False
        self.socket.xonxoff  = False
        self.socket.timeout  = 0.01
        self.version = sys.version_info[0]
        try:
            self.socket.open()
        except serial.SerialException:
            print('Could not open serial port {:s}'.format(self.socket.portstr))
            exit()

    def __del__(self):
        self.socket.close()

    def read(self):
        try:
            data = self.socket.read()
            return bytearray(data) if self.version == 2 else data
        except serial.SerialException:
            print('Serial port error')
            exit()

    def write(self, data):
        self.socket.write(data)


class NetworkStream:
    def __init__(self, networkAddress, networkPort, modemAddress=None, modemPort=None):
        try:
            verbose('Connecting to {}:{}, modem {}:{}'.format(networkAddress, networkPort,
                    modemAddress, modemPort))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((networkAddress, networkPort))
            self.socket.settimeout(0.1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            if modemAddress is not None and modemPort is not None:
                self.socket.sendall('{:d}:{:d}\n'.format(modemAddress, modemPort).encode())
        except:
            print('Network connection failed')
            exit()
        self.version = sys.version_info[0]

    def __del__(self):
        self.socket.close()

    def read(self):
        try:
            data = self.socket.recv(64)
            return bytes(data) if self.version == 2 else data
        except:
            return ''

    def write(self, data):
        self.socket.sendall(data)

class DatagramStream:
    def __init__(self, networkAddress, networkPort, modemAddress=None, modemPort=None):
        try:
            verbose('Udp {:s}:{:d}, modem {:d}:{:d}'.format(networkAddress, networkPort,
                    modemAddress, modemPort))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("0.0.0.0", networkPort))
            self.socket.settimeout(0.1)
        except:
            print('Network connection failed')
            exit()
        self.version = sys.version_info[0]
        self.address = (networkAddress,networkPort)

    def __del__(self):
        self.socket.close()

    def read(self):
        try:
            data, address = self.socket.recvfrom(64)
            return bytes(data) if self.version == 2 else data
        except:
            return ''

    def write(self, data):
        self.socket.sendto(data, self.address)


class Parser:
    class State:
        SYNC, ID, LENGTH, PAYLOAD, CHECKSUM, DONE, ERROR = range(0, 7)


    class Packet:
        def __init__(self, ident=0, data=None):
            self.id = ident
            self.data = data if data is not None else bytearray()
            self.length = len(data) if data is not None else 0


    class Counter:
        def __init__(self):
            self.received = 0
            self.errors = 0


    def __init__(self):
        self.reset()
        self.counter = Parser.Counter()

    def reset(self):
        self.state = Parser.State.SYNC
        self.packet = Parser.Packet()
        self.position = 0
        self.checksum = (0, 0)

    def process(self, data):
        for i in range(0, len(data)):
            if self.state == Parser.State.DONE or self.state == Parser.State.ERROR:
                self.reset()

            value = data[i]
            if self.state == Parser.State.SYNC:
                if self.position == 0 and chr(value) == 'p':
                    self.position += 1
                elif self.position == 1 and chr(value) == 'l':
                    self.checksum = (0, 0)
                    self.position = 0
                    self.state = Parser.State.ID
                else:
                    self.position = 0
                    self.state = Parser.State.SYNC
            elif self.state == Parser.State.ID:
                self.packet.id = value
                self.state = Parser.State.LENGTH;
            elif self.state == Parser.State.LENGTH:
                self.packet.len = value
                self.position = 0
                self.state = Parser.State.PAYLOAD if self.packet.len > 0 else Parser.State.CHECKSUM
            elif self.state == Parser.State.PAYLOAD:
                self.packet.data.append(value)
                self.position += 1
                if self.position == self.packet.len:
                    self.position = 0
                    self.state = Parser.State.CHECKSUM
            elif self.state == Parser.State.CHECKSUM:
                if self.position == 0:
                    self.checksum = (value, 0)
                    self.position += 1
                elif self.position == 1:
                    self.checksum = (self.checksum[0], value)
                    computed = Parser.crc((0, 0), bytearray([self.packet.id, self.packet.len]) + self.packet.data)
                    if self.checksum == computed:
                        self.counter.received += 1
                        self.state = Parser.State.DONE
                        return i + 1
                    else:
                        self.counter.errors += 1
                        self.state = Parser.State.ERROR

        return len(data)

    @staticmethod
    def create(ident, data):
        if len(data) > 255:
            raise Exception()

        checksum = Parser.crc((0, 0), bytearray([ident, len(data)]) + data)
        return 'pl'.encode() + bytearray([ident, len(data)]) + data + bytearray(checksum)

    @staticmethod
    def crc(previous, data):
        b1, b2 = previous
        for value in data:
            b1 = (b1 + value) & 0xFF
            b2 = (b2 + b1) & 0xFF
        return (b1, b2)


class Message:
    REQ_PARAM                      = 0x05
    PARAM_INFO                     = 0x06
    PARAM                          = 0x07
    PROTOCOL_REQUEST               = 0x22
    PROTOCOL_INFO                  = 0x23
    LICENSE_INFO_REQUEST           = 0x4B
    LICENSE_INFO                   = 0x4C
    SYSTEM_COMMAND                 = 0x36
    SYSTEM_COMMAND_RESPONSE        = 0x37
    COMPONENT_COUNT_REQUEST        = 0x29
    COMPONENT_COUNT                = 0x2A
    COMPONENT_INFO_REQUEST         = 0x2B
    COMPONENT_INFO                 = 0x2C
    COMPONENT_INFO_ERROR           = 0x2D
    COMPONENT_FIELD_REQUEST        = 0x2E
    COMPONENT_FIELD                = 0x2F
    COMPONENT_FIELD_RESPONSE       = 0x30
    COMPONENT_FIELD_DESCRIBE       = 0x31
    COMPONENT_FIELD_INFO           = 0x32
    COMPONENT_FIELD_ERROR          = 0x33
    COMPONENT_MESSAGE              = 0x38
    COMPONENT_FILE_DESCRIBE        = 0x3C
    COMPONENT_FILE_INFO            = 0x3D
    COMPONENT_FILE_INFO_ERROR      = 0x3E
    COMPONENT_FILE_WRITE           = 0x3F
    COMPONENT_FILE_WRITE_RESPONSE  = 0x40
    COMPONENT_FILE_READ            = 0x41
    COMPONENT_FILE_READ_RESPONSE   = 0x42
    COMPONENT_FILE_READ_ERROR      = 0x43
    COMPONENT_RAW_DATA             = 0x48
    COMPONENT_INFO_EXT             = 0x49
    COMPONENT_FIELD_INFO_EXT       = 0x4A
    MEDIA_PASSPORT                 = 0x44
    GO_TO_POINT_V2                 = 0x4D
    GO_TO_POINT_RESPONSE           = 0x4F
    GOTO_LOCAL_POINT               = 0x50

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return [e for e in dir(Message) if isinstance(getattr(Message, e), int)
                and getattr(Message, e) == self.value][0]

    @staticmethod
    def makeReqParam(fields):
        return struct.pack('B', fields['number'])

    @staticmethod
    def makeProtocolRequest(fields):
        return struct.pack('BB', fields['protoMajor'], fields['protoMinor'])

    @staticmethod
    def makeSystemCommand(fields):
        return struct.pack('B', fields['command'])

    @staticmethod
    def makeLicenseInfoRequest(fields):
        return bytes()

    @staticmethod
    def makeComponentCountRequest(fields):
        return bytes()

    @staticmethod
    def makeComponentInfoRequest(fields):
        return struct.pack('B', fields['component'])

    @staticmethod
    def makeComponentFieldRequest(fields):
        return struct.pack('BB', fields['component'], fields['field'])

    @staticmethod
    def makeComponentField(fields):
        payload = struct.pack('BBB', fields['component'], fields['field'], fields['type'])
        payload += Protocol.pack(fields['type'], fields['value'])
        return payload

    @staticmethod
    def makeComponentFieldDescribe(fields):
        return struct.pack('BB', fields['component'], fields['field'])

    @staticmethod
    def makeComponentFileDescribe(fields):
        return struct.pack('BBB', fields['component'], fields['file'], fields['flags'])

    @staticmethod
    def makeComponentFileWrite(fields):
        return struct.pack('<BBI', fields['component'], fields['file'], fields['position']) + fields['data']

    @staticmethod
    def makeComponentFileRead(fields):
        return struct.pack('<BBIHB', fields['component'], fields['file'], fields['position'],
                fields['length'], fields['fragment'])

    @staticmethod
    def makeParam(fields):
        payload = struct.pack('<Bf', fields['number'], fields['value'])
        payload += fields['name'].encode() + bytes([0] * (32 - len(fields['name'])))
        return payload

    @staticmethod
    def makeComponentRawData(fields):
        return struct.pack('B', fields['component']) + fields['payload']

    @staticmethod
    def makeGotoLocalPoint(fields):
        return struct.pack('iiiI', fields['x'], fields['y'], fields['z'], fields['time'])

    @staticmethod
    def makeGoToPointV2(fields):
        return struct.pack('<BiiihBBHHHH',
                fields['sequence'],
                fields['latitude'],
                fields['longitude'],
                fields['altitude'],
                fields['yaw'],
                fields['flags'],
                fields['type'],
                fields['duration'],
                fields['radius'],
                fields['onStartedCommand'],
                fields['onReachedCommand'])

    @staticmethod
    def parseParamInfo(data):
        fields = {}
        fields['id'] = Message.PARAM_INFO
        fields['count'] = data[0]
        return fields

    @staticmethod
    def parseParam(data):
        fields = {}
        fields['id'] = Message.PARAM
        fields['number'] = data[0]
        fields['value'] = struct.unpack('<f', data[1:5])[0]

        nameChunk = data[5:37]
        nameChunk = nameChunk[0:nameChunk.find(0)]
        fields['name'] = nameChunk.decode('utf-8')
        return fields

    @staticmethod
    def parseProtocolInfo(data):
        fields = {}
        fields['id'] = Message.PROTOCOL_INFO
        fields['protoMajor'] = data[0]
        fields['protoMinor'] = data[1]
        fields['firmwareVersion'] = struct.unpack('<H', data[2:4])[0]
        fields['uavType'] = data[4]
        fields['uavNumber'] = struct.unpack('<I', data[5:9])[0]
        return fields

    @staticmethod
    def parseLicenseInfo(data):
        fields = {}
        fields['id'] = Message.LICENSE_INFO
        fields['uuid'] = data[0:16]
        fields['timestamp'] = struct.unpack('<I', data[16:20])[0]
        fields['startTime'] = struct.unpack('<I', data[20:24])[0]
        fields['endTime'] = struct.unpack('<I', data[24:28])[0]
        fields['zones'] = struct.unpack('<I', data[28:32])[0]
        fields['license'] = struct.unpack('<H', data[32:34])[0]
        fields['launches'] = struct.unpack('<H', data[34:36])[0]
        fields['launchesLimit'] = struct.unpack('<H', data[36:38])[0]
        fields['active'] = data[38]
        fields['sign'] = data[39:71]
        fields['payload'] = data[:38]
        return fields

    @staticmethod
    def parseSystemCommandResponse(data):
        fields = {}
        fields['id'] = Message.SYSTEM_COMMAND_RESPONSE
        fields['command'] = data[0]
        fields['result'] = data[1]
        return fields

    @staticmethod
    def parseComponentCount(data):
        fields = {}
        fields['id'] = Message.COMPONENT_COUNT
        fields['count'] = data[0]
        return fields

    @staticmethod
    def parseComponentInfoError(data):
        fields = {}
        fields['id'] = Message.COMPONENT_INFO_ERROR
        fields['component'] = data[0]
        fields['result'] = data[1]
        return fields

    @staticmethod
    def parseComponentInfo(data):
        fields = {}
        fields['id'] = Message.COMPONENT_INFO
        fields['component'] = data[0]
        fields['type'] = data[1]
        fields['size'] = data[2]
        fields['minor'] = data[3]
        fields['revision'] = struct.unpack('<H', data[4:6])[0]
        fields['hash'] = struct.unpack('<I', data[6:10])[0]
        nameLength = data[10]
        fields['name'] = data[11:11 + nameLength].decode('utf-8')
        return fields

    @staticmethod
    def parseComponentInfoExt(data):
        fields = {}
        fields['id'] = Message.COMPONENT_INFO_EXT
        fields['component'] = data[0]
        fields['type'] = data[1]
        fields['count'] = data[2]
        fields['swMajor'] = data[3]
        fields['swMinor'] = data[4]
        fields['swRevision'] = struct.unpack('<I', data[5:9])[0]
        fields['hwMajor'] = data[9]
        fields['hwMinor'] = data[10]
        fields['hash'] = struct.unpack('<I', data[11:15])[0]
        nameLength = data[15]
        fields['name'] = data[16:16 + nameLength].decode('utf-8')
        return fields

    @staticmethod
    def parseComponentFieldError(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FIELD_ERROR
        fields['component'] = data[0]
        fields['field'] = data[1]
        fields['result'] = data[2]
        return fields

    @staticmethod
    def parseComponentFieldResponse(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FIELD_RESPONSE
        fields['component'] = data[0]
        fields['field'] = data[1]
        fields['result'] = data[2]
        return fields

    @staticmethod
    def parseComponentFieldInfo(data):
        fields = {}
        position = 0
        fields['id'] = Message.COMPONENT_FIELD_INFO

        fields['component'] = data[position]
        position += 1

        fields['field'] = data[position]
        position += 1

        fields['type'] = data[position]
        position += 1

        nameLength = data[position]
        fields['name'] = data[position + 1:position + 1 + nameLength].decode('utf-8')
        position += 1 + nameLength

        fields['scale'] = int.from_bytes(data[position:position + 1], byteorder='big', signed=True)
        position += 1

        unitLength = data[position]
        fields['unit'] = data[position + 1:position + 1 + unitLength].decode('utf-8')
        position += 1 + unitLength

        fields['min'], fields['max'] = Protocol.unpack(fields['type'], data[position:], 2)

        return fields

    @staticmethod
    def parseComponentFieldInfoExt(data):
        fields = {}
        position = 0
        fields['id'] = Message.COMPONENT_FIELD_INFO_EXT

        fields['component'] = data[position]
        position += 1

        fields['field'] = data[position]
        position += 1

        fields['type'] = data[position]
        position += 1

        fields['size'] = data[position]
        position += 1

        fields['flags'] = data[position]
        position += 1

        fields['scale'] = int.from_bytes(data[position:position + 1], byteorder='big', signed=True)
        position += 1

        nameLength = data[position]
        fields['name'] = data[position + 1:position + 1 + nameLength].decode('utf-8')
        position += 1 + nameLength

        unitLength = data[position]
        fields['unit'] = data[position + 1:position + 1 + unitLength].decode('utf-8')
        position += 1 + unitLength

        if fields['size'] > 1:
            minMaxValues = Protocol.unpack(fields['type'], data[position:], 2 * fields['size'])
            fields['min'] = tuple(minMaxValues[0:fields['size']])
            fields['max'] = tuple(minMaxValues[fields['size']:2 * fields['size']])
        else:
            fields['min'], fields['max'] = Protocol.unpack(fields['type'], data[position:], 2)

        return fields

    @staticmethod
    def parseComponentField(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FIELD
        fields['component'] = data[0]
        fields['field'] = data[1]
        fields['type'] = data[2]

        try:
            count = int((len(data) - 3) / Protocol.typeToSize(fields['type']))
            fields['value'] = Protocol.unpack(fields['type'], data[3:], count)
        except:
            fields['value'] = None

        return fields

    @staticmethod
    def parseComponentFileInfo(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FILE_INFO
        fields['component'] = data[0]
        fields['file'] = data[1]
        fields['status'] = data[2]
        fields['size'] = struct.unpack('<I', data[3:7])[0]
        fields['checksum'] = struct.unpack('<I', data[7:11])[0]
        return fields

    @staticmethod
    def parseComponentFileInfoError(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FILE_INFO_ERROR
        fields['component'] = data[0]
        fields['file'] = data[1]
        fields['result'] = data[2]
        return fields

    @staticmethod
    def parseComponentFileWriteResponse(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FILE_WRITE_RESPONSE
        fields['component'] = data[0]
        fields['file'] = data[1]
        fields['position'] = struct.unpack('<I', data[2:6])[0]
        fields['result'] = data[6]
        return fields

    @staticmethod
    def parseComponentFileReadResponse(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FILE_READ_RESPONSE
        fields['component'] = data[0]
        fields['file'] = data[1]
        fields['position'] = struct.unpack('<I', data[2:6])[0]
        fields['data'] = data[6:]
        return fields

    @staticmethod
    def parseComponentFileReadError(data):
        fields = {}
        fields['id'] = Message.COMPONENT_FILE_READ_ERROR
        fields['component'] = data[0]
        fields['file'] = data[1]
        fields['position'] = struct.unpack('<I', data[2:6])[0]
        fields['result'] = data[6]
        return fields

    @staticmethod
    def parseComponentMessage(data):
        fields = {}
        fields['id'] = Message.COMPONENT_MESSAGE
        fields['component'] = data[0]
        fields['type'] = data[1]
        fields['payload'] = data[2:]
        return fields

    @staticmethod
    def parseComponentRawData(data):
        fields = {}
        fields['id'] = Message.COMPONENT_RAW_DATA
        fields['component'] = data[0]
        fields['payload'] = data[1:]
        return fields

    @staticmethod
    def parseGoToPointResponse(data):
        fields = {}
        fields['id'] = Message.GO_TO_POINT_RESPONSE
        fields['sequence'] = data[0]
        return fields

class Result:
    INCORRECT_PARAMETER = -3
    CHECKSUM_ERROR      = -2
    GENERIC_TIMEOUT     = -1

    SUCCESS             = 0
    COMPONENT_NOT_FOUND = 1
    FIELD_NOT_FOUND     = 2
    FIELD_TYPE_MISMATCH = 3
    FIELD_RANGE_ERROR   = 4
    FIELD_ERROR         = 5
    FIELD_READ_ONLY     = 6
    FILE_NOT_FOUND      = 7
    FILE_ERROR          = 8
    FIELD_UNAVAILABLE   = 9
    FIELD_TIMEOUT       = 10
    FILE_ACCESS_ERROR   = 11
    FILE_POSITION_ERROR = 12
    FILE_TIMEOUT        = 13
    QUEUE_ERROR         = 14
    COMMAND_UNSUPPORTED = 15
    COMMAND_QUEUED      = 16
    COMMAND_ERROR       = 17
    HWID_MISMATCH       = 18
    LICENSE_EXPIRED     = 19
    SIGNATURE_ERROR     = 20

    def __init__(self, value):
        self.value = value

    def __str__(self):
        try:
            return [e for e in dir(Result) if not e.startswith('__') and getattr(Result, e) == self.value][0]
        except:
            return 'UNKNOWN_ERROR'


class CommandError(Exception):
    def __init__(self, value):
        super(CommandError, self).__init__(str(Result(value)))
        self.value = value


class CommandTimeout(CommandError):
    def __init__(self):
        CommandError.__init__(self, Result.GENERIC_TIMEOUT)


class ChecksumError(CommandError):
    def __init__(self):
        CommandError.__init__(self, Result.CHECKSUM_ERROR)


class IncorrectParameter(CommandError):
    def __init__(self):
        CommandError.__init__(self, Result.INCORRECT_PARAMETER)


class UavType:
    NAMES = {
            0: 'GeoScan 101 3S',
            1: 'GeoScan 300',
            2: 'GeoScan 002',
            4: 'GeoScan 401',
            5: 'GeoScan 102',
            6: 'GeoScan 201 4S',
            7: 'GeoScan 301',
            8: 'GeoScan 425',
            9: 'GeoScan 501',
            10: 'GeoScan 101 4S',
            11: 'GeoScan 201 5S',
            12: 'GeoScan Pioneer',
            13: 'GeoScan 201M',
            14: 'GeoScan 501M',
    }

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return UavType.NAMES[self.value] if self.value in UavType.NAMES else 'Undefined'


class Protocol:
    SYSTEM_COMMANDS = {
            1: 'Start baro calibration',
            3: 'Start gyro calibration',
            4: 'Start mag calibration',
            5: 'Stop mag calibration',
            6: 'Start accel calibration',
            7: 'Stop accel calibration',
            8: 'Make accel sample',
            9: 'Reset board alignment',
            10: 'Align board',
            11: 'Start mag check',
            12: 'Stop mag check',
            13: 'Recalc mag declination',
            14: 'Format memory',
            15: 'Start gyro check',
            18: 'Restart',
            19: 'Restart to bootloader',
            20: 'Run IMU self-test'
    }

    @staticmethod
    def isIntType(typeValue):
        return typeValue >= 2 and typeValue <= 9

    @staticmethod
    def isSignedType(typeValue):
        return typeValue >= 2 and typeValue <= 5

    @staticmethod
    def isUnsignedType(typeValue):
        return typeValue >= 6 and typeValue <= 9

    @staticmethod
    def isFloatType(typeValue):
        return typeValue >= 10 and typeValue <= 11

    @staticmethod
    def stringToValue(typeValue, typeSize, text):
        if typeValue == 1:
            return text
        else:
            parts = [part for part in text.split(' ') if len(part) > 0]
            output = None

            if len(parts) != typeSize:
                return None

            if typeValue == 0: # bool
                output = [True if part in ('True', 'true', '1', 'on') else False for part in parts]
            elif typeValue in (10, 11): # float or double
                try:
                    output = [float(part) for part in parts]
                except:
                    return None
            else:
                # Signed and unsigned integers
                try:
                    output = []
                    for part in parts:
                        base = 16 if len(part) > 2 and part[0:2] == '0x' else 10
                        output.append(int(part, base))
                except:
                    return None

            return output[0] if len(output) == 1 else output

    @staticmethod
    def typeToFormat(typeValue):
        # Bool values are unsupported by struct package
        return {1: 'b', 2: 'b', 3: 'h', 4: 'i', 5: 'q', 6: 'B', 7: 'H', 8: 'I', 9: 'Q', 10: 'f', 11: 'd'}[typeValue]

    @staticmethod
    def typeToSize(typeValue):
        # Pure magic, see protocol documentation
        return {0: 1, 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 2, 8: 4, 9: 8, 10: 4, 11: 8}[typeValue]

    @staticmethod
    def typeToString(typeValue):
        return {
                0: 'bool',
                1: 'char',
                2: 'int8',
                3: 'int16',
                4: 'int32',
                5: 'int64',
                6: 'uint8',
                7: 'uint16',
                8: 'uint32',
                9: 'uint64',
                10: 'float',
                11: 'double'}[typeValue]

    @staticmethod
    def unpack(typeValue, data, count=1):
        if typeValue in (0, 1): # bool or char
            if count > len(data):
                return tuple((None for i in range(0, count)))

            if typeValue == 0: # bool
                return tuple([data[i] != 0 for i in range(0, count)])
            else: # char
                return tuple([chr(data[i]) for i in range(0, count)])

        try:
            typeSize = Protocol.typeToSize(typeValue)
            if len(data) >= count * typeSize:
                typeFormat = '<' + ('' if count == 1 else str(count)) + Protocol.typeToFormat(typeValue)
                return tuple(struct.unpack(typeFormat, data[0:typeSize * count])[0:count])
            else:
                return tuple((None for i in range(0, count)))
        except:
            return tuple((None for i in range(0, count)))

    @staticmethod
    def pack(typeValue, value, count=1):
        if typeValue == 1: # char or string
            return value.encode('utf-8')
        else:
            try:
                count = len(value)
                package = value
            except:
                count = 1
                package = [value]

            if typeValue == 0: # bool
                return bytes([1 if entry else 0 for entry in package])
            else:
                # Exception during typeToFormat will mean an error in message preparation
                typeFormat = '<{:d}{:s}'.format(count, Protocol.typeToFormat(typeValue))

                if typeValue in (10, 11):
                    # Float and double
                    return struct.pack(typeFormat, *package)
                else:
                    # Signed and unsigned integers
                    return struct.pack(typeFormat, *package)


class StreamHandler:
    inputParsers = {
            Message.PARAM_INFO:                    Message.parseParamInfo,
            Message.PARAM:                         Message.parseParam,
            Message.PROTOCOL_INFO:                 Message.parseProtocolInfo,
            Message.LICENSE_INFO:                  Message.parseLicenseInfo,
            Message.SYSTEM_COMMAND_RESPONSE:       Message.parseSystemCommandResponse,
            Message.COMPONENT_MESSAGE:             Message.parseComponentMessage,
            Message.COMPONENT_COUNT:               Message.parseComponentCount,
            Message.COMPONENT_INFO:                Message.parseComponentInfo,
            Message.COMPONENT_INFO_EXT:            Message.parseComponentInfoExt,
            Message.COMPONENT_INFO_ERROR:          Message.parseComponentInfoError,
            Message.COMPONENT_FIELD:               Message.parseComponentField,
            Message.COMPONENT_FIELD_RESPONSE:      Message.parseComponentFieldResponse,
            Message.COMPONENT_FIELD_INFO:          Message.parseComponentFieldInfo,
            Message.COMPONENT_FIELD_INFO_EXT:      Message.parseComponentFieldInfoExt,
            Message.COMPONENT_FIELD_ERROR:         Message.parseComponentFieldError,
            Message.COMPONENT_FILE_INFO:           Message.parseComponentFileInfo,
            Message.COMPONENT_FILE_INFO_ERROR:     Message.parseComponentFileInfoError,
            Message.COMPONENT_FILE_WRITE_RESPONSE: Message.parseComponentFileWriteResponse,
            Message.COMPONENT_FILE_READ_RESPONSE:  Message.parseComponentFileReadResponse,
            Message.COMPONENT_FILE_READ_ERROR:     Message.parseComponentFileReadError,
            Message.COMPONENT_RAW_DATA:            Message.parseComponentRawData,
            Message.GO_TO_POINT_RESPONSE:          Message.parseGoToPointResponse,
    }

    outputParsers = {
            Message.REQ_PARAM:                Message.makeReqParam,
            Message.PROTOCOL_REQUEST:         Message.makeProtocolRequest,
            Message.SYSTEM_COMMAND:           Message.makeSystemCommand,
            Message.LICENSE_INFO_REQUEST:     Message.makeLicenseInfoRequest,
            Message.COMPONENT_COUNT_REQUEST:  Message.makeComponentCountRequest,
            Message.COMPONENT_INFO_REQUEST:   Message.makeComponentInfoRequest,
            Message.COMPONENT_FIELD_REQUEST:  Message.makeComponentFieldRequest,
            Message.COMPONENT_FIELD:          Message.makeComponentField,
            Message.COMPONENT_FIELD_DESCRIBE: Message.makeComponentFieldDescribe,
            Message.COMPONENT_FILE_DESCRIBE:  Message.makeComponentFileDescribe,
            Message.COMPONENT_FILE_WRITE:     Message.makeComponentFileWrite,
            Message.COMPONENT_FILE_READ:      Message.makeComponentFileRead,
            Message.PARAM:                    Message.makeParam,
            Message.COMPONENT_RAW_DATA:       Message.makeComponentRawData,
            Message.GO_TO_POINT_V2:           Message.makeGoToPointV2,
            Message.GOTO_LOCAL_POINT:         Message.makeGotoLocalPoint
    }

    def __init__(self, stream):
        self.parser = Parser()
        self.stream = stream
        self.callbacks = []

        self.stats = {}
        [self.stats.update({key: 0}) for key in StreamHandler.inputParsers]
        [self.stats.update({key: 0}) for key in StreamHandler.outputParsers]
        self.rates = []
        self.sent = 0
        self.rx, self.tx = 0, 0

        self.terminate = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def getMessageCounters(self):
        return (self.parser.counter.received, self.sent, self.parser.counter.errors)

    def getMessageRates(self):
        return copy.deepcopy(self.rates)

    def getMessageStats(self):
        return copy.deepcopy(self.stats)

    def send(self, fields):
        if 'id' not in fields or fields['id'] not in StreamHandler.outputParsers:
            # User application tries to send incorrect message
            raise Exception()

        payload = StreamHandler.outputParsers[fields['id']](fields)
        packet = Parser.create(fields['id'], payload)
        self.stream.write(packet)

        # Gather statistics
        self.sent += 1
        self.stats[fields['id']] += 1
        self.tx += len(packet)

        debug('TX: ' + str(fields))

    def stop(self):
        self.terminate = True
        self.thread.join()

    def run(self):
        timestamp = time.time()

        while not self.terminate:
            data = self.stream.read()

            self.rx += len(data)
            while len(data) > 0:
                count = self.parser.process(data)
                data = data[count:]

                if self.parser.state == Parser.State.DONE:
                    ident, payload = self.parser.packet.id, self.parser.packet.data
                    if ident in StreamHandler.inputParsers:
                        self.stats[ident] += 1
                        fields = StreamHandler.inputParsers[ident](payload)
                        debug('RX: ' + str(fields))
                        for callback in self.callbacks:
                            callback(fields)
                    else:
                        debug('RX: unknown message, class {:02X}, length {:d}'.format(ident, len(payload)))

            if time.time() > timestamp + 1.0:
                self.rates = ([(self.rx, self.tx)] + self.rates)[:60]
                self.rx, self.tx = 0, 0
                timestamp = time.time()


class Field:
    READABLE, WRITABLE, IMPORTANT = 0x01, 0x02, 0x04
    MASK = READABLE | WRITABLE | IMPORTANT

    def __init__(self, component, index):
        self.component = component
        self.index = index
        self.type = None
        self.size = 1
        self.name = ''
        self.flags = Field.MASK
        self.scale = 0
        self.unit = ''
        self.min = None
        self.max = None
        self.value = None

    @staticmethod
    def flagsToString(flags):
        return ('R' if flags & 1 != 0 else '-') + ('W' if flags & 2 != 0 else '-') + ('I' if flags & 4 != 0 else '-')

    def readInfo(self, callback=None, blocking=True):
        proxyCallback = lambda packet: listen(
                (
                        Message.COMPONENT_FIELD_INFO,
                        Message.COMPONENT_FIELD_INFO_EXT,
                        Message.COMPONENT_FIELD_ERROR
                ),
                packet, lambda fields: self.onFieldInfoReceived(fields, callback))
        request = {'id': Message.COMPONENT_FIELD_DESCRIBE, 'component': self.component.address, 'field': self.index}

        if not blocking or callback is not None:
            self.component.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.component.messenger.invoke(packet=request, callback=proxyCallback)
            if response is None:
                raise CommandError(Result.GENERIC_TIMEOUT)
            if response['id'] == Message.COMPONENT_FIELD_ERROR:
                raise CommandError(response['result'])

    def onFieldInfoReceived(self, fields, callback=None):
        if fields['component'] == self.component.address and fields['field'] == self.index:
            if fields['id'] != Message.COMPONENT_FIELD_ERROR:
                self.type = fields['type']
                self.name = fields['name']
                self.scale = fields['scale']
                self.unit = fields['unit']
                self.min = fields['min']
                self.max = fields['max']

                if fields['id'] == Message.COMPONENT_FIELD_INFO_EXT:
                    self.size = fields['size']
                    self.flags = fields['flags']

                if callback is not None:
                    callback(self, Result(Result.SUCCESS))
            else:
                if callback is not None:
                    callback(self, Result(fields['result']))

            return True
        else:
            return False

    def read(self, callback=None, blocking=True):
        proxyCallback = lambda packet: listen((Message.COMPONENT_FIELD, Message.COMPONENT_FIELD_RESPONSE), packet,
                lambda fields: self.onFieldRead(fields, callback))
        request = {'id': Message.COMPONENT_FIELD_REQUEST, 'component': self.component.address,
                'field': self.index, 'type': self.type}

        if not blocking or callback is not None:
            self.component.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.component.messenger.invoke(packet=request, callback=proxyCallback)
            if response is None:
                raise CommandError(Result.GENERIC_TIMEOUT)
            if response['id'] != Message.COMPONENT_FIELD:
                raise CommandError(response['result'])
            return response['value']

    def onFieldRead(self, fields, callback=None):
        if fields['component'] == self.component.address and fields['field'] == self.index:
            completed = fields['id'] == Message.COMPONENT_FIELD

            if completed:
                self.value = fields['value'] if self.size > 1 else fields['value'][0]
            if callback is not None:
                if completed:
                    callback(self, Result(Result.SUCCESS), self.value)
                else:
                    callback(self, Result(fields['result']), None)
            return True
        else:
            return False

    def write(self, value, callback=None, blocking=True):
        proxyCallback = lambda packet: listen(Message.COMPONENT_FIELD_RESPONSE, packet,
                lambda fields: self.onFieldWritten(value, fields, callback))
        request = {'id': Message.COMPONENT_FIELD, 'component': self.component.address,
                'field': self.index, 'type': self.type, 'value': value}

        if not blocking or callback is not None:
            self.component.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.component.messenger.invoke(packet=request, callback=proxyCallback)
            if response is None:
                raise CommandError(Result.GENERIC_TIMEOUT)
            if response['result'] != Result.SUCCESS:
                raise CommandError(response['result'])

    def onFieldWritten(self, value, fields, callback=None):
        if fields['component'] == self.component.address and fields['field'] == self.index:
            if fields['result'] == Result.SUCCESS:
                self.value = value
            if callback is not None:
                callback(self, Result(fields['result']), self.value)
            return True
        else:
            return False


class File:
    class RequestState:
        def __init__(self):
            self.checksum = 0
            self.result = Result(Result.SUCCESS)
            self.position = 0
            self.total = 0
            self.retries = 0
            self.sem = threading.Semaphore(0)
            self.timeout = False
            self.data = bytes()


    def __init__(self, component, index, status=0):
        self.component = component
        self.index = index
        self.status = status
        self.state = None
        self.data = None

    @staticmethod
    def flagsToString(flags):
        return ('R' if flags & 1 != 0 else '-') + ('W' if flags & 2 != 0 else '-')

    def readFileInfo(self, verify=False, callback=None, blocking=True):
        flags = 0x03 if verify else 0x01

        proxyCallback = lambda packet: listen((Message.COMPONENT_FILE_INFO, Message.COMPONENT_FILE_INFO_ERROR),
                packet, lambda fields: self.onFileInfoReceived(fields, callback))
        request = {'id': Message.COMPONENT_FILE_DESCRIBE, 'component': self.component.address,
                'file': self.index, 'flags': flags}

        if not blocking or callback is not None:
            self.component.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.component.messenger.invoke(packet=request, callback=proxyCallback)
            if response is None:
                raise CommandError(Result.GENERIC_TIMEOUT)
            if response['id'] != Message.COMPONENT_FILE_INFO:
                raise CommandError(response['result'])
            return (response['size'], response['checksum'])

    def onFileInfoReceived(self, fields, callback=None):
        if fields['component'] == self.component.address and fields['file'] == self.index:
            if fields['id'] == Message.COMPONENT_FILE_INFO:
                self.status = fields['status']
                if callback is not None:
                    callback(self, Result(Result.SUCCESS), (fields['size'], fields['checksum']))
            else:
                if callback is not None:
                    callback(self, Result(fields['result']), {})
            return True
        else:
            return False

    def readFileChunk(self, position, chunkSize, burstSize):
        if chunkSize == 0 or burstSize == 0:
            # Incorrect settings
            raise Exception()

        request = {'id': Message.COMPONENT_FILE_READ, 'component': self.component.address, 'file': self.index,
                'position': position, 'length': int(chunkSize * burstSize), 'fragment': chunkSize}
        self.component.messenger.invoke(packet=request)

    def onFileChunkRead(self, state, fields):
        if fields['component'] == self.component.address and fields['file'] == self.index:
            if fields['id'] == Message.COMPONENT_FILE_READ_RESPONSE:
                if fields['position'] == state.position:
                    chunk = fields['data']
                    debug('File {:d}:{:d} chunk [{:06X}:{:06X}] appended'.format(self.component.address,
                            self.index, state.position, state.position + len(chunk)))

                    state.retries = 0
                    state.data[state.position:state.position + len(chunk)] = chunk
                    state.position += len(chunk)
                else:
                    debug('File {:d}:{:d} chunk [{:06X}:{:06X}] dropped'.format(self.component.address,
                            self.index, fields['position'], fields['position'] + len(fields['data'])))
            else:
                verbose('File {:d}:{:d} at {:d} error {:s} ({:d})'.format(self.component.address, self.index,
                        fields['position'], str(Result(fields['result'])), fields['result']))

                if fields['result'] not in (Result.FILE_TIMEOUT, Result.QUEUE_ERROR):
                    state.result = Result(fields['result'])
            state.sem.release()
            return True
        else:
            return False

    @staticmethod
    def onFileChunkTimeout(state):
        state.timeout = True
        state.sem.release()

    def getProgress(self):
        state = self.state
        if state is not None:
            progress = float(state.position) / state.total if state.total > 0 else 1.0
            return (progress, state.position, state.total)
        else:
            return (1.0, 0, 0)

    def read(self, chunkSize=48, burstSize=4, verify=False, callback=None):
        request = Messenger.FileReadRequest(self, chunkSize, burstSize, verify, callback)
        self.component.messenger.invokeAsync(request=request)

    def readImpl(self, chunkSize, burstSize, verify):
        state = File.RequestState()

        # Request file size and, optionally, file checksum
        state.total, state.checksum = self.readFileInfo(verify)

        if state.total > 0:
            callback = lambda packet: listen((Message.COMPONENT_FILE_READ_RESPONSE, Message.COMPONENT_FILE_READ_ERROR),
                    packet, lambda fields: self.onFileChunkRead(state, fields))
            position = 0
            timer = None

            state.data = bytearray([0] * state.total)
            self.state = state
            self.component.messenger.subscribe(callback)

            while state.position < state.total and state.result.value == Result.SUCCESS:
                if state.timeout:
                    state.timeout = False
                    state.retries += 1
                    debug('File {:d}:{:d} data timeout {:d}/{:d}/{:d} iteration {:d}'.format(self.component.address,
                            self.index, state.position, position, state.total, state.retries))
                    if state.retries < self.component.messenger.defaultRetryCount:
                        position = state.position
                    else:
                        state.result = Result(Result.GENERIC_TIMEOUT)
                        break

                if position < state.total and position - state.position < int(chunkSize * burstSize / 2):
                    nextChunkSize = min(chunkSize * burstSize, state.total - position)
                    if nextChunkSize > chunkSize:
                        # Read as much aligned chunks as possible
                        nextChunkSize = nextChunkSize - nextChunkSize % chunkSize
                        self.readFileChunk(position, chunkSize, nextChunkSize / chunkSize)
                    else:
                        # Read last unaligned chunk
                        self.readFileChunk(position, nextChunkSize, 1)

                    if timer is not None:
                        timer.cancel()
                    timer = threading.Timer(self.component.messenger.defaultTimeout, File.onFileChunkTimeout, [state])
                    timer.start()
                    position += nextChunkSize

                state.sem.acquire()

            if timer is not None:
                timer.cancel()
            self.component.messenger.forget(callback)
            self.state = None

        if state.result.value == Result.GENERIC_TIMEOUT:
            raise CommandTimeout()
        if state.result.value != Result.SUCCESS:
            raise CommandError(state.result.value)

        if verify and state.checksum != (binascii.crc32(state.data) & 0xFFFFFFFF):
            raise ChecksumError()

        self.data = bytearray(state.data)

    def sendSpecialWriteSeq(self, position, timeout):
        # Send restart or finalize sequences
        proxyCallback = lambda packet: listen(Message.COMPONENT_FILE_WRITE_RESPONSE, packet,
                self.onFileWriteResponseReceived)
        request = {'id': Message.COMPONENT_FILE_WRITE, 'component': self.component.address,
                'file': self.index, 'position': position, 'data': bytes()}
        response = self.component.messenger.invoke(packet=request, callback=proxyCallback, timeout=timeout)

        if response['result'] != Result.SUCCESS:
            raise CommandError(response['result'])

    def finalizeWrite(self, total):
        timeout = self.component.messenger.defaultTimeout * self.component.messenger.defaultWriteMult
        self.sendSpecialWriteSeq(total if total > 0 else 0xFFFFFFFF, timeout)
        debug('File {:d}:{:d} finalized at {:d}'.format(self.component.address, self.index, total))

    def restartWrite(self):
        timeout = self.component.messenger.defaultTimeout * self.component.messenger.defaultWriteMult
        self.sendSpecialWriteSeq(0, timeout)
        debug('File {:d}:{:d} write restarted'.format(self.component.address, self.index))

    def onFileWriteResponseReceived(self, fields):
        return fields['component'] == self.component.address and fields['file'] == self.index

    def writeFileChunk(self, position, data):
        if len(data) == 0:
            # Chunk length should be greater than zero
            raise Exception()

        timeout = self.component.messenger.defaultTimeout * self.component.messenger.defaultWriteMult
        request = {'id': Message.COMPONENT_FILE_WRITE, 'component': self.component.address, 'file': self.index,
                'position': position, 'data': data}
        self.component.messenger.invoke(packet=request, timeout=timeout)

    def onFileChunkWritten(self, chunkSize, state, fields):
        if fields['component'] == self.component.address and fields['file'] == self.index:
            if fields['result'] == Result.SUCCESS:
                if fields['position'] >= state.position:
                    expectedChunkSize = min(chunkSize, state.total - fields['position'])
                    debug('File {:d}:{:d} chunk [{:06X}:{:06X}] committed'.format(self.component.address,
                            self.index, state.position, fields['position'] + expectedChunkSize))

                    state.retries = 0
                    state.position = fields['position'] + expectedChunkSize
                else:
                    debug('File {:d}:{:d} chunk at {:d} reordered'.format(self.component.address,
                            self.index, fields['position']))
            else:
                verbose('File {:d}:{:d} at {:d} error {:s} ({:d})'.format(self.component.address, self.index,
                        fields['position'], str(Result(fields['result'])), fields['result']))

                if fields['result'] in (Result.FILE_ERROR, Result.FILE_TIMEOUT, Result.QUEUE_ERROR):
                    state.retries += 1

                    if state.retries < self.component.messenger.defaultRetryCount:
                        # Rewind file position to a previously committed one
                        state.timeout = True
                    else:
                        # No retries left, propagate error to the main thread
                        state.result = Result(fields['result'])
                else:
                    state.result = Result(fields['result'])
            state.sem.release()
            return True
        else:
            return False

    def write(self, data, chunkSize=48, burstSize=4, append=False, verify=True, callback=None):
        request = Messenger.FileWriteRequest(self, data, chunkSize, burstSize, append, verify, callback)
        self.component.messenger.invokeAsync(request=request)

    def writeImpl(self, data, chunkSize, burstSize, append, verify):
        state = File.RequestState()

        if append:
            # In append mode file size should be requested first
            position, checksum = self.readFileInfo(verify=verify)
            offset = position
            if verify:
                expectedChecksum = binascii.crc32(data, checksum) & 0xFFFFFFFF
            state.position = position
            state.total = position + len(data)
        else:
            self.restartWrite()
            position = 0
            offset = 0
            if verify:
                expectedChecksum = binascii.crc32(data, 0) & 0xFFFFFFFF
            state.total = len(data)

        callback = lambda packet: listen(Message.COMPONENT_FILE_WRITE_RESPONSE, packet,
                lambda fields: self.onFileChunkWritten(chunkSize, state, fields))
        timer = None

        self.data = None
        self.state = state
        self.component.messenger.subscribe(callback)

        while state.position < state.total and state.result.value == Result.SUCCESS:
            if state.timeout:
                state.timeout = False
                state.retries += 1
                debug('File {:d}:{:d} data timeout {:d}/{:d}/{:d} iteration {:d}'.format(self.component.address,
                        self.index, state.position, position, state.total, state.retries))
                if state.retries < self.component.messenger.defaultRetryCount:
                    position = state.position
                else:
                    state.result = Result(Result.GENERIC_TIMEOUT)
                    break

            while position < state.total and position - state.position < int(chunkSize * burstSize / 2):
                nextChunkSize = min(chunkSize, state.total - position)
                self.writeFileChunk(position, data[position - offset:position - offset + nextChunkSize])

                if timer is not None:
                    timer.cancel()
                timer = threading.Timer(self.component.messenger.defaultTimeout, File.onFileChunkTimeout, [state])
                timer.start()
                position += nextChunkSize

            state.sem.acquire()

        if timer is not None:
            timer.cancel()
        self.component.messenger.forget(callback)
        self.state = None

        if state.result.value == Result.GENERIC_TIMEOUT:
            raise CommandTimeout()
        elif state.result.value != Result.SUCCESS:
            raise CommandError(state.result.value)

        if not append:
            self.finalizeWrite(state.total)

        if verify:
            size, checksum = self.readFileInfo(verify=True)
            if size != state.total or checksum != expectedChecksum:
                raise ChecksumError()

        if not append:
            self.data = data


class Component:
    HEALTH_OK, HEALTH_WARNING, HEALTH_ERROR, HEALTH_CRITICAL = range(0, 4)
    MODE_OPERATIONAL, MODE_INITIALIZATION, MODE_MAINTENANCE, MODE_SOFTWARE_UPDATE, MODE_OFFLINE = 0, 1, 2, 3, 7

    def __init__(self, messenger, address):
        self.messenger = messenger
        self.address = address
        self.name = ''
        self.hash = 0
        self.type = 0
        self.swVersion = (0, 0, 0)
        self.hwVersion = (0, 0)
        self.count = 0
        self.fields = {}
        self.files = {}
        self.mutex = threading.Lock()
        self.flagField = None

        # Callback for automatic component messages
        self.onFieldsChanged = None

    def __del__(self):
        self.messenger.forget(self.componentMessageCallback)

    def __getitem__(self, item):
        try:
            index = int(item)
            self.mutex.acquire()
            entry = self.fields[index] if index in self.fields else None
            self.mutex.release()
            return entry
        except:
            entry = None
            self.mutex.acquire()
            for i in self.fields:
                if self.fields[i].name == item:
                    entry = self.fields[i]
                    break
            self.mutex.release()
            return entry

    def uid(self):
        # TODO Detect different file configurations
        ident = self.name + str(self.count) + str(self.hash)\
                + str(self.swVersion[0]) + str(self.swVersion[1]) + str(self.swVersion[2])\
                + str(self.hwVersion[0]) + str(self.hwVersion[1])
        generator = hashlib.md5()
        generator.update(ident.encode())
        return generator.hexdigest()

    @staticmethod
    def parseFlags(value):
        if value is not None:
            restart = value & (1 << 26) != 0
            mode = (value >> 27) & 7
            health = (value >> 30) & 3

            return (mode, health, restart)
        else:
            return None

    def getStatus(self):
        ''' Returns tuple of two elements when a device status is available or None:
        (mode, health) -- device mode and device health
        None           -- status is unavailable
        '''

        if self.flagField is not None:
            status = Component.parseFlags(self.flagField.value)
            return (status[0], status[1]) if status is not None else None
        else:
            return None

    def onFieldAttached(self, field):
        if field.name == 'flags' and self.flagField is None:
            self.flagField = field

    def loadComponentDescription(self, description):
        self.mutex.acquire()
        for entry in description['fields']:
            field = Field(self, entry['field'])
            field.type = entry['type']
            field.size = entry['size']
            field.flags = entry['flags']
            field.name = entry['name']
            field.scale = entry['scale']
            field.unit = entry['unit']
            field.min = entry['min']
            field.max = entry['max']
            verbose('\tField {:3d} "{:s}": type {:s}, size {:d}, flags {:s}, scale {:d}, unit "{:s}", range [{}:{}]'.format(
                    field.index, field.name, Protocol.typeToString(field.type), field.size,
                    Field.flagsToString(field.flags), field.scale, field.unit, field.min, field.max))
            self.fields[entry['field']] = field
            self.onFieldAttached(self.fields[entry['field']])
        for entry in description['files']:
            stream = File(self, entry['file'], entry['status'])
            verbose('\tFile {:d}: flags {:s}'.format(stream.index, File.flagsToString(stream.status)))
            self.files[entry['file']] = stream
        self.mutex.release()

    def makeComponentDescription(self):
        fields, files = [], []
        self.mutex.acquire()
        for i in self.fields:
            field = self.fields[i]
            fields.append({'field': i, 'type': field.type, 'size': field.size, 'flags': field.flags,
                    'name': field.name, 'scale': field.scale, 'unit': field.unit, 'min': field.min, 'max': field.max})
        for i in self.files:
            stream = self.files[i]
            files.append({'file': i, 'status': stream.status})
        self.mutex.release()
        return {'fields': fields, 'files': files}

    def readInfo(self, callback=None, blocking=True):
        proxyCallback = lambda packet: listen(
                (
                        Message.COMPONENT_INFO,
                        Message.COMPONENT_INFO_EXT,
                        Message.COMPONENT_INFO_ERROR
                ),
                packet, lambda fields: self.onComponentInfoReceived(fields, callback))
        request = {'id': Message.COMPONENT_INFO_REQUEST, 'component': self.address}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback)
            if response is not None and response['id'] == Message.COMPONENT_INFO_ERROR:
                raise CommandError(response['result'])

    def onComponentInfoReceived(self, fields, callback=None):
        if fields['component'] == self.address:
            if fields['id'] != Message.COMPONENT_INFO_ERROR:
                self.type = fields['type']
                self.hash = fields['hash']
                self.name = fields['name']

                if fields['id'] == Message.COMPONENT_INFO_EXT:
                    self.count = fields['count']
                    self.swVersion = (fields['swMajor'], fields['swMinor'], fields['swRevision'])
                    self.hwVersion = (fields['hwMajor'], fields['hwMinor'])
                else:
                    self.count = fields['size']
                    self.swVersion = (fields['type'], fields['minor'], fields['revision'])
                    self.hwVersion = (1, 0)

                self.messenger.subscribe(self.componentMessageCallback)

                if callback is not None:
                    callback(self, Result(Result.SUCCESS))
            else:
                if callback is not None:
                    callback(self, Result(fields['result']))
            return True
        else:
            return False

    def readFieldInfo(self):
        allFieldsReceived = True
        for i in range(0, self.count):
            try:
                field = Field(self, i)
                field.readInfo()

                verbose('\tField {:3d} "{:s}": type {:s}, size {:d}, flags {:s}, scale {:d}, unit "{:s}", range [{}:{}]'.format(
                        i, field.name, Protocol.typeToString(field.type), field.size,
                        Field.flagsToString(field.flags), field.scale, field.unit, field.min, field.max))

                self.mutex.acquire()
                self.fields[i] = field
                self.onFieldAttached(self.fields[i])
                self.mutex.release()
            except CommandError as e:
                verbose('\tField {:3d} read info failed: {:s}'.format(i, str(e)))
                allFieldsReceived = False
                break
            except CommandTimeout:
                verbose('\tField {:3d} read info timeout'.format(i))
                allFieldsReceived = False
                break
        return allFieldsReceived

    def readFileInfo(self, start=0, end=8):
        indices = list(range(start, end + 1)) + [255]
        for i in indices:
            try:
                stream = File(self, i)
                stream.readFileInfo()
                verbose('\tFile {:d}: flags {:s}'.format(stream.index, File.flagsToString(stream.status)))

                self.mutex.acquire()
                self.files[i] = stream
                self.mutex.release()
            except CommandTimeout:
                break
            except CommandError:
                pass

    def parseComponentMessagePayload(self, payload):
        offset = 0
        updatedFields = []
        verbose('Message from component {:d} "{:s}"'.format(self.address, self.name))

        self.mutex.acquire()
        while offset < len(payload):
            number = payload[offset]
            if number in self.fields:
                field = self.fields[number]
                value = Protocol.unpack(field.type, payload[offset + 1:])
                if value is None:
                    break
                value = value if field.size > 1 else value[0]
                field.value = value
                verbose('\tField {:3d} "{:s}": {}'.format(number, field.name, value))
                offset += 1 + Protocol.typeToSize(field.type)
                updatedFields.append(number)
            else:
                verbose('\tField {:3d} not found'.format(number))
                break
        self.mutex.release()
        return updatedFields

    def componentMessageCallback(self, fields):
        if fields['id'] == Message.COMPONENT_MESSAGE and fields['component'] == self.address:
            updatedFields = self.parseComponentMessagePayload(fields['payload'])
            if self.onFieldsChanged is not None:
                self.onFieldsChanged(self.address, updatedFields)
        return False

    def readFields(self, callback=None, blocking=True):
        if callback is not None:
            proxyCallback = lambda field, result, value: callback()
        elif not blocking:
            proxyCallback = lambda field, result, value: None
        else:
            proxyCallback = None

        entries = list(self.fields.values())

        if len(entries) > 0:
            for entry in entries[:-1]:
                entry.read(blocking=False)
            entries[-1].read(proxyCallback)
        elif callback is not None:
            callback()

    # FIXME
    # def findFilesAsync(self, start, end):
    #     self.files = {}
    #     for i in range(start, end + 1):
    #         stream = File(self, i)
    #         info = stream.
    #         self.readFileInfoAsync(i)


class Hub:
    def __init__(self, messenger, cache=None):
        self.messenger = messenger
        self.cache = cache
        self.count = 0
        self.components = {}
        self.parameters = {}
        self.mutex = threading.Lock()
        self.onFieldsChanged = None

        self.version = (0, 0, 0)
        self.model = 255
        self.lic = None

        if self.cache is not None and not os.path.isdir(self.cache):
            os.mkdir(self.cache)

    def __getitem__(self, item):
        try:
            address = int(item)
            self.mutex.acquire()
            entry = self.components[address] if address in self.components else None
            self.mutex.release()
            return entry
        except:
            entry = None
            self.mutex.acquire()
            for i in self.components:
                if self.components[i].name == item:
                    entry = self.components[i]
                    break
            self.mutex.release()
            return entry

    def connect(self):
        self.mutex.acquire()
        self.components = {}
        self.mutex.release()

        try:
            info = self.getProtocolInfo()
            self.version = info[0]
            self.model = info[1]
        except:
            print('error in get protocol info')
            return

        # try:
        #     info = self.getProtocolInfo()
        #     self.version = info[0]
        #     self.model = info[1]
        # except:
        #     return

        try:
            self.lic = self.getLicenseInfo()
        except:
            verbose('License Info read failed')
            print('license failed')

        try:
            self.getComponentCount()
        except:
            print('failed to get component count')
            return

        for i in range(0, self.count):
            try:
                component = Component(self.messenger, i)
                component.readInfo()

                verbose('Component {:d} "{:s}": count {:d}, type {:d}, software {:d}.{:d}.{:d}, hardware {:d}.{:d}, hash {:08X}'.format(
                        i, component.name, component.count, component.type,
                        component.swVersion[0], component.swVersion[1], component.swVersion[2],
                        component.hwVersion[0], component.hwVersion[1], component.hash))

                component.onFieldsChanged = self.onComponentFieldsChanged
                self.mutex.acquire()
                self.components[i] = component
                self.mutex.release()

                loadedFromCache = False
                print(f'cache is ----{self.cache}')
                if self.cache is not None:
                    try:
                        cachedDescriptionName = os.path.join(self.cache, self.components[i].uid() + '.json')
                        with open(cachedDescriptionName, 'rb') as js_fd:
                            descriptionData = js_fd.read() 
                        description = json.loads(descriptionData.decode())
                        verbose('\tComponent info loaded from cache')
                        print('[message] Component info loaded from cache')
                        self.components[i].loadComponentDescription(description)
                        loadedFromCache = True
                    except:
                        pass
                if not loadedFromCache and self.components[i].readFieldInfo():
                    self.components[i].readFileInfo()

                    if self.cache is not None:
                        cachedDescriptionName = os.path.join(self.cache, self.components[i].uid() + '.json')
                        description = self.components[i].makeComponentDescription()
                        with open(cachedDescriptionName, 'wb') as cache_fd:
                            cache_fd.write(json.dumps(description).encode())
            except CommandError as e:
                verbose('Component {:d} read info failed: {:s}'.format(i, str(e)))
                print('Component {:d} read info failed: {:s}'.format(i, str(e)))
            except CommandTimeout:
                verbose('Component {:d} read info timeout'.format(i))
                print('Component {:d} read info timeout'.format(i))

    def clearParamList(self):
        self.parameters = {}

    def getParamList(self):
        self.parameters = {}
        for i in range(0, self.getParamCount()):
            param = self.getParam(i)
            if param is not None:
                self.parameters[i] = (param[0], param[1])
                verbose('Parameter {:d} "{:s}", value {:g}'.format(i, param[0], param[1]))
            else:
                break

    def getParamCount(self, callback=None, blocking=True):
        ''' Return values:
        Count -- parameter count or zero in case of error
        '''
        return self.getParam(0xFF, callback, blocking)

    def getParam(self, number, callback=None, blocking=True):
        proxyCallback = lambda packet: listen((Message.PARAM, Message.PARAM_INFO), packet,
                lambda fields: self.onParamReceived(value=None, fields=fields, callback=callback, number=number))
        request = {'id': Message.REQ_PARAM, 'number': number}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback)
            return None
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback)
            if number != 0xFF:
                if response['id'] == Message.PARAM:
                    return (response['name'], response['value'])
                else:
                    raise IncorrectParameter()
            else:
                return response['count'] if response is not None else 0

    def setParam(self, value, name='', number=None, callback=None, blocking=True):
        if name != '':
            if number is not None:
                raise Exception()
            number = 0
            proxyCallback = lambda packet: listen((Message.PARAM, Message.PARAM_INFO), packet,
                    lambda fields: self.onParamReceived(value=value, fields=fields, callback=callback, name=name))
        elif number is not None:
            proxyCallback = lambda packet: listen((Message.PARAM, Message.PARAM_INFO), packet,
                    lambda fields: self.onParamReceived(value=value, fields=fields, callback=callback, number=number))
        else:
            raise Exception()

        request = {'id': Message.PARAM, 'number': number, 'name': name, 'value': value}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback)
            if response['id'] == Message.PARAM_INFO:
                raise IncorrectParameter()

    def getParamCount(self, callback=None, blocking=True):
        return self.getParam(0xFF, callback, blocking)

    def onParamReceived(self, value, fields, callback=None, number=None, name=None):
        if number is not None and name is not None:
            raise Exception()

        if fields['id'] == Message.PARAM_INFO:
            if number is not None:
                # Count request or get/set by number
                if number == 0xFF:
                    # Parameter count request
                    if callback is not None:
                        # Notify about parameter count
                        callback(fields['count'])
                else:
                    # Parameter read request
                    if callback is not None:
                        # Read failed, return None
                        callback(number, None)
                return True
            else:
                # Is not our request, ignore
                return False
        elif fields['id'] == Message.PARAM:
            if (number is not None and number == fields['number']) or (name is not None and name == fields['name']):
                if value is None or math.isclose(a=value, b=fields['value'], rel_tol=1e-5):
                    # Read or write completed successfully
                    self.parameters[fields['number']] = (fields['name'], fields['value'])
                    if callback is not None:
                        callback(number, fields['value'])
                else:
                    # Write failed
                    if callback is not None:
                        callback(number, None)
                return True
            else:
                return False
        else:
            return False

    def getComponentCount(self, callback=None, blocking=True):
        proxyCallback = lambda packet: listen(Message.COMPONENT_COUNT, packet,
                lambda fields: self.onComponentCountReceived(fields, callback))
        request = {'id': Message.COMPONENT_COUNT_REQUEST}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback)
            return response['count']

    def onComponentCountReceived(self, fields, callback=None):
        self.count = fields['count']
        if callback is not None:
            callback(fields['count'])
        return True

    def getProtocolInfo(self, version=(1, 6), callback=None, blocking=True):
        proxyCallback = lambda packet: listen(Message.PROTOCOL_INFO, packet,
                lambda fields: self.onProtocolInfoReceived(fields, callback))
        request = {'id': Message.PROTOCOL_REQUEST, 'protoMajor': version[0], 'protoMinor': version[1]}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback)
            return ((response['protoMajor'], response['protoMinor'], response['firmwareVersion']),
                    response['uavType'], response['uavNumber'])

    def onProtocolInfoReceived(self, fields, callback=None):
        self.version = (fields['protoMajor'], fields['protoMinor'])
        if callback is not None:
            callback(((fields['protoMajor'], fields['protoMinor'], fields['firmwareVersion']),
                    fields['uavType'], fields['uavNumber']))
        return True

    def getLicenseInfo(self, callback=None, blocking=True):
        proxyCallback = lambda packet: listen(Message.LICENSE_INFO, packet,
                lambda fields: self.onLicenseInfoReceived(fields, callback))
        request = {'id': Message.LICENSE_INFO_REQUEST}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback, retries=4)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback, retries=4)
            if response is not None:
                return {key:response[key] for key in response if key != 'id'}
            else:
                return None

    def onLicenseInfoReceived(self, fields, callback=None):
        if callback is not None:
            callback({key:fields[key] for key in fields if key != 'id'})
        return True

    def onComponentFieldsChanged(self, component, fields):
        if self.onFieldsChanged is not None:
            self.onFieldsChanged(component, fields)

    def sendCommand(self, code, callback=None, blocking=True):
        TIMEOUT_TABLE = {
                # 256 barometer samples at 50 Hz + default timeout
                1: 5.12 + self.messenger.defaultTimeout,
                # 1024 gyroscope samples at 100 Hz + default timeout
                3: 10.24 + self.messenger.defaultTimeout,
                # 256 accelerometer samples at 100 Hz + default timeout
                8: 2.56 + self.messenger.defaultTimeout,
                # 1024 gyroscope samples at 100 Hz + default timeout
                15: 10.24 + self.messenger.defaultTimeout,
                # 4 steps, 0.5 seconds for each step, up to 2.0 seconds for sleep overhead on 1 kHz + default timeout
                20: 4.0 + self.messenger.defaultTimeout
        }

        try:
            timeout = TIMEOUT_TABLE[code]
        except:
            timeout = self.messenger.defaultTimeout

        proxyCallback = lambda packet: listen(Message.SYSTEM_COMMAND_RESPONSE, packet,
                lambda fields: self.onCommandResponseReceived(fields, callback))
        request = {'id': Message.SYSTEM_COMMAND, 'command': code}

        if not blocking or callback is not None:
            self.messenger.invokeAsync(packet=request, callback=proxyCallback, retries=1, timeout=timeout)
        else:
            response = self.messenger.invoke(packet=request, callback=proxyCallback, retries=1, timeout=timeout)
            return Result(response['result']) if response is not None else Result(Result.GENERIC_TIMEOUT)

    def onCommandResponseReceived(self, fields, callback=None):
        if callback is not None:
            callback(fields['command'], Result(fields['result']))
        return True

    def getMessageCounters(self):
        return self.messenger.handler.getMessageCounters()

    def getMessageLatency(self):
        latency = self.messenger.latency
        return float(sum(latency)) / len(latency) if len(latency) > 0 else 0.0

    def getMessageRates(self):
        return self.messenger.handler.getMessageRates()

    def getMessageStats(self):
        return self.messenger.handler.getMessageStats()

    def getLicense(self):
        return self.lic

    def paramFromInf(self, data):
        try:
            paramStrings = [s.split('=') for s in data.split('\n') if not s.startswith('#') and len(s) > 0]
            paramTuples = [(s[0], float(s[1])) for s in paramStrings if len(s) == 2]
            return paramTuples
        except ValueError:
            return None

    def paramToInf(self):
        params = list(self.parameters.values())
        params.sort(key=lambda x: x[0])
        data = '#\n#{:s}\n'.format(time.asctime())
        for param in params:
            data += '{:s}={}\n'.format(*param)
        return data

class Messenger:
    class CommandState:
        def __init__(self):
            self.sem = threading.Semaphore(0)
            self.response = None


    class GenericRequest:
        def __init__(self, messenger, packet, callback, retries, timeout):
            self.messenger = messenger
            self.packet = packet
            self.callback = callback
            self.retries = retries
            self.timeout = timeout

        def handle(self):
            if self.callback is None:
                self.messenger.send(self.packet)
            else:
                for i in range(0, self.retries):
                    response = Messenger.GenericRequest.genericHandler(self.messenger,
                            self.packet, self.callback, self.timeout)
                    if response is not None:
                        break

        @staticmethod
        def genericHandler(messenger, packet, callback, timeout):
            def waitForCompletion(state, timeout):
                timer = threading.Timer(timeout, lambda state: state.sem.release(), [state])
                timer.start()
                state.sem.acquire()
                endTime = time.time()
                timer.cancel()

            state = Messenger.CommandState()
            proxyCallback = lambda fields: Messenger.messageCallback(state, callback, fields)

            # Send command
            startTime = time.time()
            messenger.send(packet, proxyCallback)

            # First stage: wait for answer
            waitForCompletion(state, timeout)
            endTime = time.time()

            # Second stage: if command was queued, wait for deferred answer
            try:
                if state.response['result'] == Result.COMMAND_QUEUED:
                    timeout -= endTime - startTime
                    waitForCompletion(state, timeout)
                    endTime = time.time()
            except:
                pass

            # Clean state
            messenger.forget(proxyCallback)

            if state.response is not None:
                messenger.latency = ([endTime - startTime] + messenger.latency)[:100]
            return state.response


    class FileRequest:
        def __init__(self, stream, chunkSize, burstSize, callback):
            self.stream = stream
            self.chunkSize = chunkSize
            self.burstSize = burstSize
            self.callback = callback


    class FileReadRequest(FileRequest):
        def __init__(self, stream, chunkSize, burstSize, verify, callback):
            Messenger.FileRequest.__init__(self, stream, chunkSize, burstSize, callback)
            self.verify = verify

        def getProgress(self):
            return self.stream.getProgress()

        def handle(self):
            try:
                self.stream.readImpl(self.chunkSize, self.burstSize, self.verify)
                result = Result(Result.SUCCESS)
            except CommandError as e:
                result = Result(e.value)

            if self.callback is not None:
                self.callback(self.stream, result)


    class FileWriteRequest(FileRequest):
        def __init__(self, stream, data, chunkSize, burstSize, append, verify, callback):
            Messenger.FileRequest.__init__(self, stream, chunkSize, burstSize, callback)
            self.data = data
            self.append = append
            self.verify = verify

        def getProgress(self):
            return self.stream.getProgress()

        def handle(self):
            try:
                self.stream.writeImpl(self.data, self.chunkSize, self.burstSize, self.append, self.verify)
                result = Result(Result.SUCCESS)
            except CommandError as e:
                result = Result(e.value)

            if self.callback is not None:
                self.callback(self.stream, result)


    def __init__(self, stream, cache=None):
        self.terminate = False
        self.requests = []
        self.requestSem = threading.Condition(threading.Lock())
        self.latency = []

        # Common protocol settings
        self.defaultRetryCount = 4
        self.defaultTimeout = 0.25
        self.defaultWriteMult = 64

        # Helpers for progress bar drawing
        self.requestCount = 0
        self.currentRequest = None

        self.handler = StreamHandler(stream)
        self.hub = Hub(self, cache)
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def __getitem__(self, item):
        return self.hub[item]

    def connect(self):
        self.hub.connect()

    def forget(self, callback):
        if callback in self.handler.callbacks:
            self.handler.callbacks.remove(callback)

    def send(self, message, callback=None):
        if callback is not None:
            self.subscribe(callback)
        self.handler.send(message)

    def subscribe(self, callback):
        if callback not in self.handler.callbacks:
            self.handler.callbacks.append(callback)

    def stop(self):
        self.handler.stop()

        self.terminate = True
        self.thread.join()

    def invoke(self, packet, callback=None, retries=None, timeout=None):
        if callback is None:
            self.send(packet)
            return None
        else:
            if retries is None:
                retries = self.defaultRetryCount
            if timeout is None:
                timeout = self.defaultTimeout

            for i in range(0, retries):
                response = Messenger.GenericRequest.genericHandler(self, packet, callback, timeout)
                debug(str(response))
                if response is not None:
                    return response

    def invokeAsync(self, packet=None, request=None, callback=None, retries=None, timeout=None):
        self.requestSem.acquire()
        if packet is not None:
            if retries is None:
                retries = self.defaultRetryCount
            if timeout is None:
                timeout = self.defaultTimeout

            self.requests.append(Messenger.GenericRequest(self, packet, callback, retries, timeout))
        elif request is not None:
            self.requests.append(request)
        else:
            raise Exception()
        self.requestCount += 1
        self.requestSem.notify()
        self.requestSem.release()

    def resetProgress(self):
        self.requestCount = len(self.requests)

    def getProgress(self):
        request = self.currentRequest
        if isinstance(request, Messenger.GenericRequest):
            total = self.requestCount
            count = min(len(self.requests), total)
            completed = total - count
            progress = float(completed) / total if total > 0 else 1.0
            return (progress, completed, total)
        elif isinstance(request, Messenger.FileReadRequest) or isinstance(request, Messenger.FileWriteRequest):
            return request.getProgress()
        else:
            return (1.0, 0, 0)

    def run(self):
        while not self.terminate:
            with self.requestSem:
                self.requestSem.wait(0.1)

            while len(self.requests) > 0:
                self.currentRequest = self.requests[0]
                self.requests = self.requests[1:]
                self.currentRequest.handle()
                self.currentRequest = None

    @staticmethod
    def messageCallback(state, callback, fields):
        if callback(fields):
            state.response = fields
            state.sem.release()
