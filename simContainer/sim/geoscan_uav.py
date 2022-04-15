#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import proto
import weakref


class Event:
    ALL                = 255
    COPTER_LANDED      = 26
    LOW_VOLTAGE1       = 31
    LOW_VOLTAGE2       = 32
    POINT_REACHED      = 42
    POINT_DECELERATION = 43
    TAKEOFF_COMPLETE   = 51
    ENGINES_STARTED    = 56
    SHOCK              = 65

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return [ev for ev in dir(Event) if isinstance(getattr(Event, ev), int)
            and getattr(Event, ev) == self.value][0]

    def __eq__(self, other):
        if self.value == other:
            return True

class Handler:
    def __init__(self, uav):
        self.uav = weakref.ref(uav)
        self.name = 'FlightManager'

        self.uav().messenger.hub.onFieldsChanged = self.on_fields_changed
        self.watchers = []

    def on_fields_changed(self, device, fields):
        device_object = self.uav().messenger.hub[device]
        if device_object.name == self.name:
            if len(fields) > 0 and device_object[fields[0]].name == 'event':
                # Read event number
                ev = device_object['event'].value
                if ev != Event.ALL:
                    # Clear event
                    device_object['event'].write(value=ev, callback=None, blocking=False)

                    for watcher in self.watchers:
                        if watcher[0] == Event.ALL or watcher[0] == ev:
                            watcher[1](Event(ev))

    def subscribe(self, callback, event):
        self.watchers.append((event, callback))

    def unsubscribe(self, callback, event):
        for i, watcher in enumerate(self.watchers):
            if watcher[0] == event and watcher[1] == callback:
                del self.watchers[i]
                break


class Gpio:
    def __init__(self, uav):
        self.uav = weakref.ref(uav)
        self.name = 'LedBar'

    def cargo(self, state=None):
        try:
            if state is None:
                self.uav().messenger.hub[self.name]['cargo'].read()
            else:
                self.uav().messenger.hub[self.name]['cargo'].write(state)
            return True
        except:
            return False


class Led:
    def __init__(self, uav):
        self.uav = weakref.ref(uav)
        self.name = 'LedBar'

    def rgb(self, color, number=None):
        clamp = lambda v: min(max(int(v), 0), 255)
        r = clamp(color[0] * 255.0)
        g = clamp(color[1] * 255.0)
        b = clamp(color[2] * 255.0)

        value = r | (g << 8) | (b << 16)
        value = (value | (0xFF << 24)) if number is None else (value | clamp(number) << 24)
        try:
            self.uav().messenger.hub[self.name]['color'].write(value)
            return True
        except:
            return False


class GlobalNavSystem:
    def __init__(self, uav):
        self.uav = uav
        self.name = 'Ublox'

    def position(self):
        try:
            lat = self.uav().messenger.hub[self.name]['latitude'].read()
            lon = self.uav().messenger.hub[self.name]['longitude'].read()
            alt = self.uav().messenger.hub[self.name]['altitude'].read()
            return (lat[0] / 1e7, lon[0] / 1e7, alt[0] / 1e3)
        except:
            return None

    def velocity(self):
        try:
            n = self.uav().messenger.hub[self.name]['latitude'].read()
            e = self.uav().messenger.hub[self.name]['longitude'].read()
            d = self.uav().messenger.hub[self.name]['altitude'].read()
            return (n[0] / 1e2, e[0] / 1e2, d[0] / 1e2)
        except:
            return None

    def satellites(self):
        try:
            gps = self.uav().messenger.hub[self.name]['satGps'].read()[0]
        except:
            gps = 0

        try:
            glonass = self.uav().messenger.hub[self.name]['satGlonass'].read()[0]
        except:
            glonass = 0

        return {'GPS': gps, 'GLONASS': glonass}

    def status(self):
        try:
            s = self.uav().messenger.hub[self.name]['status'].read()
            return s
        except:
            return None


class LocalNavSystem:
    def __init__(self, uav):
        self.uav = uav
        self.name = 'USNav_module'

    def position(self):
        try:
            x = self.uav().messenger.hub[self.name]['x'].read()
            y = self.uav().messenger.hub[self.name]['y'].read()
            z = self.uav().messenger.hub[self.name]['z'].read()
            return (x[0], y[0], z[0])
        except:
            return None

    def velocity(self):
        try:
            x = self.uav().messenger.hub[self.name]['velX'].read()
            y = self.uav().messenger.hub[self.name]['velY'].read()
            z = self.uav().messenger.hub[self.name]['velZ'].read()
            return (x[0], y[0], z[0])
        except:
            return None

    def status(self):
        try:
            return self.uav().messenger.hub[self.name]['status'].read()
        except:
            return None


class Sensors:
    def __init__(self, uav):
        self.uav = weakref.ref(uav)
        self.gnss = GlobalNavSystem(self.uav)
        self.lps = LocalNavSystem(self.uav)

    def accel(self):
        try:
            ax = self.uav().messenger.hub['SensorMonitor']['accelX'].read()
            ay = self.uav().messenger.hub['SensorMonitor']['accelY'].read()
            az = self.uav().messenger.hub['SensorMonitor']['accelZ'].read()
            return (ax[0] / 1e3, ay[0] / 1e3, az[0] / 1e3)
        except:
            return None

    def gyro(self):
        try:
            gx = self.uav().messenger.hub['SensorMonitor']['gyroX'].read()
            gy = self.uav().messenger.hub['SensorMonitor']['gyroY'].read()
            gz = self.uav().messenger.hub['SensorMonitor']['gyroZ'].read()
            return (gx[0] / 1e3, gy[0] / 1e3, gz[0] / 1e3)
        except:
            return None

    def mag(self):
        try:
            mx = self.uav().messenger.hub['SensorMonitor']['magX'].read()
            my = self.uav().messenger.hub['SensorMonitor']['magY'].read()
            mz = self.uav().messenger.hub['SensorMonitor']['magZ'].read()
            return (mx[0] / 1e3, my[0] / 1e3, mz[0] / 1e3)
        except:
            return None

    def altitude(self):
        try:
            alt = self.uav().messenger.hub['UavMonitor']['altitude'].read()
            return alt[0] / 1e3
        except:
            return None

    def orientation(self):
        try:
            r = self.uav().messenger.hub['UavMonitor']['roll'].read()
            p = self.uav().messenger.hub['UavMonitor']['pitch'].read()
            y = self.uav().messenger.hub['UavMonitor']['yaw'].read()
            return (r[0] / 1e2, p[0] / 1e2, y[0] / 1e2)
        except:
            return None

    def range(self):
        try:
            alt = self.uav().messenger.hub['SensorMonitor']['optFlowRange'].read()
            return alt[0] / 1e3
        except:
            return None


class Control:
    def __init__(self, uav):
        self.uav = weakref.ref(uav)
        self.global_point_seq = 0

    def disarm(self):
        try:
            self.uav().messenger.hub['UavMonitor']['mode'].write(2)
            return True
        except:
            return False

    def landing(self):
        try:
            self.uav().messenger.hub['UavMonitor']['mode'].write(23)
            return True
        except:
            return False

    def make_go_to_global_point_fields(self, type, flags, position, duration, radius, yaw):
        fields = {}
        fields['id'] = proto.Message.GO_TO_POINT_V2
        fields['sequence'] = self.global_point_seq
        fields['latitude'] = int(position[0] * 1e7)
        fields['longitude'] = int(position[1] * 1e7)
        fields['altitude'] = int(position[2] * 1e2)
        fields['yaw'] = int(yaw)
        fields['flags'] = flags
        fields['type'] = type
        fields['duration'] = int(duration / 3.75)
        if fields['duration'] > 65535:
            fields['duration'] = 65535
        fields['radius'] = int(radius)
        fields['onStartedCommand'] = 0xFFFF
        fields['onReachedCommand'] = 0xFFFF

        self.global_point_seq += 1
        if self.global_point_seq >= 256:
            self.global_point_seq = 0

        return fields

    def preflight(self):
        try:
            self.uav().messenger.hub['UavMonitor']['mode'].write(10)
            return True
        except:
            return False

    def set_yaw(self, yaw):
        try:
            self.uav().messenger.hub['ManualControl']['yawManual'].write(int(yaw * 100.0))
            return True
        except:
            return False

    def takeoff(self):
        try:
            self.uav().messenger.hub['UavMonitor']['mode'].write(12)
            return True
        except:
            return False

    def to_global_point(self, position):
        callback = lambda packet: proto.listen(proto.Message.GO_TO_POINT_RESPONSE, packet)
        request = self.make_go_to_global_point_fields(
            type=3,
            flags=0,
            position=position,
            duration=0.0,
            radius=0.0,
            yaw=0.0)

        response = self.uav().messenger.invoke(packet=request, callback=callback)
        if response is None:
            return False
        else:
            return True
            
    def go_manual_22mode(self, northSpeed, eastSpeed, downSpeed, yawSpeed, interval):
        try:
            self.uav().messenger.hub['ManualControl']['northSpeed'].write(northSpeed)
            self.uav().messenger.hub['ManualControl']['eastSpeed'].write(eastSpeed)
            self.uav().messenger.hub['ManualControl']['downSpeed'].write(downSpeed)
            self.uav().messenger.hub['ManualControl']['yawSpeed'].write(yawSpeed)
            self.uav().messenger.hub['ManualControl']['altitude'].write(0)
            self.uav().messenger.hub['ManualControl']['speed'].write(0)
            self.uav().messenger.hub['ManualControl']['interval'].write(interval)
            self.uav().messenger.hub['ManualControl']['mode'].write(5)
        except:
            return False
        return True

    def to_local_point(self, position, time=0):
        fields = {}
        fields['id'] = proto.Message.GOTO_LOCAL_POINT
        fields['x'] = position[0]
        fields['y'] = position[1]
        fields['z'] = position[2]
        fields['time'] = int(time)

        self.uav().messenger.invoke(packet=fields)

    def rtl(self):
        try:
            self.uav().messenger.hub['UavMonitor']['mode'].write(18)
            return True
        except:
            return False


class UAV:
    def __init__(self, serial=None, baudrate=57600, tcp=None, udp=None, modem=None, cache='cache'):
        if serial is not None:
            stream = proto.SerialStream(serial, baudrate)
        elif tcp is not None:
            try:
                parts = tcp.split(':')
                if len(parts) == 1:
                    address, port = parts[0], 5500
                else:
                    address, port = parts[0], int(parts[1])

                if modem is not None:
                    parts = modem.split(':')
                    modem_address, modem_port = int(parts[0]), int(parts[1])
                else:
                    modem_address, modem_port = None, None
                stream = proto.NetworkStream(address, port, modem_address, modem_port)
            except:
                print('Incorrect TCP arguments')
                exit()
        elif udp is not None:
            # TODO
            raise Exception()
        else:
            print('No connection type specified')
            raise Exception()

        self.messenger = proto.Messenger(stream, cache)
        self.sensors = Sensors(self)
        self.control = Control(self)
        self.gpio = Gpio(self)
        self.led = Led(self)
        self.handler = Handler(self)

        # proto.debugEnabled = True
        # proto.verboseEnabled = True

    def __del__(self):
        self.messenger.stop()

    def connect(self):
        self.messenger.connect()

    def disconnect(self):
        self.messenger.stop()

    def time(self):
        try:
            UNIX_TO_GPS = 315964800
            gps_time = self.messenger.hub['UavMonitor']['time'].read()[0]
            return float(gps_time) / 1000000.0 + 315964800.0
        except:
            return None

    def uptime(self):
        try:
            return self.messenger.hub['UavMonitor']['uptime'].read()[0]
        except:
            return None

    def flight_time(self):
        try:
            return self.messenger.hub['FlightManager']['missionTime'].read()[0]
        except:
            return None

    def subscribe(self, callback, event=Event.ALL):
        self.handler.subscribe(callback, event)

    def unsubscribe(self, callback, event=Event.ALL):
        self.handler.unsubscribe(callback, event)
