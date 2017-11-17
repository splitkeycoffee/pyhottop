"""
Interface with the hottop roaster through the serial port.
"""

import binascii
import datetime
import glob
import logging
import serial
import sys
import time

py2 = sys.version[0] == '2'

if py2:
    from Queue import Queue
else:
    import queue as queue

from threading import Thread, Event


class InvalidInput(Exception):
    """Exception to capture invalid input commands."""
    pass


class SerialConnectionError(Exception):
    """Exception to capture serial connection issues."""
    pass


def bool2int(bool):
    """Convert a bool to an int."""
    if bool:
        return 1
    else:
        return 0


def now_time():
    """Get the current time."""
    return datetime.datetime.now()


def hex2int(value):
    """Convert hex to an int."""
    return int(binascii.hexlify(value), 16)


def celsius2fahrenheit(c):
    """Convert temperatures."""
    return (c * 1.8) + 32


class ControlProcess(Thread):

    """Primary processor to communicate with the hottop directly.

    :param conn: Established serial connection to the Hottop
    :type conn: Serial instance
    :param config: Initial configurations settings
    :type config: dict
    :param q: Shared queue to interact with the user interface
    :type q: Queue instance
    :param logger: Shared logger to keep continuity
    :type logger: Logging instance
    :param callback: Optional callback function to stream results
    :type callback: function
    :returns: ControlProces instance
    """

    def __init__(self, conn, config, q, logger, callback=None):
        """Extend threads to support more control logic."""
        Thread.__init__(self)
        self._conn = conn
        self._log = logger
        self._config = config
        self._q = q
        self._cb = callback
        self._retry_count = 0

        # Trigger events used in the core loop.
        self.cooldown = Event()
        self.exit = Event()

    def _generate_config(self):
        """Generate a configuration that can be sent to the Hottop roaster.

        Configuration settings need to be represented inside of a byte array
        that is then written to the serial interface. Much of the configuration
        is static, but control settings are also included and pulled from the
        shared dictionary.

        :returns: Byte array of the prepared configuration.
        """
        config = bytearray([0x00]*36)
        config[0] = 0xA5
        config[1] = 0x96
        config[2] = 0xB0
        config[3] = 0xA0
        config[4] = 0x01
        config[5] = 0x01
        config[6] = 0x24
        config[10] = self._config.get('heater', 0)
        config[11] = self._config.get('fan', 0)
        config[12] = self._config.get('main_fan', 0)
        config[16] = self._config.get('solenoid', 0)
        config[17] = self._config.get('drum_motor', 0)
        config[18] = self._config.get('cooling_motor', 0)
        config[35] = sum([b for b in config[:35]]) & 0xFF
        return bytes(config)

    def _send_config(self):
        """Send configuration data to the hottop.

        :returns: bool
        :raises: Generic exceptions if an error is identified.
        """
        serialized = self._generate_config()
        self._log.debug("Configuration has been serialized")
        try:
            self._conn.flushInput()
            self._conn.flushOutput()
            self._conn.write(serialized)
            return True
        except Exception as e:
            self._log.error(e)
            raise Exception(e)

    def _validate_checksum(self, buffer):
        """Validate the buffer response against the checksum.

        When reading the serial interface, data will come back in a raw format
        with an included checksum process.

        :returns: bool
        """
        self._log.debug("Validating the buffer")
        if len(buffer) == 0:
            self._log.debug("Buffer was empty")
            return False
        p0 = hex2int(buffer[0])
        p1 = hex2int(buffer[1])
        checksum = sum([hex2int(c) for c in buffer[:35]]) & 0xFF
        p35 = hex2int(buffer[35])
        if p0 != 165 or p1 != 150 or p35 != checksum:
            self._log.debug("Buffer checksum was not valid")
            return False
        return True

    def _read_settings(self, retry=True):
        """Read the information from the Hottop.

        Read the settings from the serial interface and convert them into a
        human-readable format that can be shared back to the end-user. Reading
        from the serial interface will occasionally produce strange results or
        blank reads, so a retry process has been built into the function as a
        recursive check.

        :returns: dict
        """
        if not self._conn.isOpen():
            self._conn.open()
        self._conn.flushInput()
        self._conn.flushOutput()
        buffer = self._conn.read(36)
        check = self._validate_checksum(buffer)
        if not check and (retry and self._retry_count < 3):
            if self._retry_count > 3:
                self._read_settings(retry=False)
            else:
                self._read_settings(retry=True)
            self._retry_count += 1
            return False

        settings = dict()
        settings['heater'] = hex2int(buffer[10])
        settings['fan'] = hex2int(buffer[11])
        settings['main_fan'] = hex2int(buffer[12])
        et = hex2int(buffer[23] + buffer[24])
        settings['external_temp'] = celsius2fahrenheit(et)
        bt = hex2int(buffer[25] + buffer[26])
        settings['bean_temp'] = celsius2fahrenheit(bt)
        settings['solenoid'] = hex2int(buffer[16])
        settings['drum_motor'] = hex2int(buffer[17])
        settings['cooling_motor'] = hex2int(buffer[18])
        settings['chaff_tray'] = hex2int(buffer[19])
        self._retry_count = 0
        return settings

    def _wake_up(self):
        """Wake the machine up to avoid race conditions.

        When first interacting with the Hottop, the machine may not wake up
        right away which can put our reader into a death loop. This wake up
        routine ensures we prime the roaster with some data before starting
        our main loops to read/write data.

        :returns: None
        """
        for range in (0, 10):
            self._send_config()
            time.sleep(self._config['interval'])

    def run(self):
        """Run the core loop of reading and writing configurations.

        This is where all the roaster magic occurs. On the initial run, we
        prime the roaster with some data to wake it up. Once awoke, we check
        our shared queue to identify if the user has passed any updated
        configuration. Once checked, start to read and write to the Hottop
        roaster as long as the exit signal has not been set. All steps are
        repeated after waiting for a specific time interval.

        There are also specialized routines built into this function that are
        controlled via events. These events are unique to the roasting process
        and pre-configure the system with a configuration, so the user doesn't
        need to do it themselves.

        :returns: None
        """
        self._wake_up()

        while not self._q.empty():
            self._config = self._q.get()

        while not self.exit.is_set():
            settings = self._read_settings()
            self._cb(settings)

            if self.cooldown.is_set():
                self._log.debug("Cool down process triggered")
                self._config['drum_motor'] = 0
                self._config['heater'] = 0
                self._config['solenoid'] = 1
                self._config['cooling_motor'] = 1
                self._config['main_fan'] = 10

            self._send_config()
            time.sleep(self._config['interval'])

    def drop(self):
        """Register a drop event to begin the cool-down process.

        :returns: None
        """
        self._log.debug("Dropping the coffee")
        self.cooldown.set()

    def shutdown(self):
        """Register a shutdown event to stop interacting with the Hottop.

        :returns: None
        """
        self._log.debug("Shutdown initiated")
        self.exit.set()


class Hottop:

    """Object to interact and control the hottop roaster.

    :returns: Hottop instance
    """

    NAME = "HOTTOP"
    USB_PORT = "/dev/cu.usbserial-DA01PEYC"
    BAUDRATE = 115200
    BYTE_SIZE = 8
    PARITY = "N"
    STOPBITS = 1
    TIMEOUT = 1
    LOG_LEVEL = logging.DEBUG
    INTERVAL = 0.5

    def __init__(self):
        """Start of the hottop."""
        self._log = self._logger()
        self._conn = None
        self._roast = list()
        self._roasting = False
        self._roast_start = None
        self._roast_end = None
        self._config = dict()
        self._q = Queue()
        self._init_controls()

    def _logger(self):
        """Create a logger to be used between processes.

        :returns: Logging instance.
        """
        logger = logging.getLogger(self.NAME)
        logger.setLevel(self.LOG_LEVEL)
        shandler = logging.StreamHandler(sys.stdout)
        fmt = '\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():'
        fmt += '%(lineno)d %(asctime)s\033[0m| %(message)s'
        shandler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(shandler)
        return logger

    def _autodiscover_usb(self):
        """Attempt to find the serial adapter for the hottop.

        This will loop over the USB serial interfaces looking for a connection
        that appears to match the naming convention of the Hottop roaster.

        :returns: string
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/cu.*')
        else:
            raise EnvironmentError('Unsupported platform')

        match = None
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                if (port.find("/dev/cu.usbserial-") > -1 and
                        port.find('bluetooth') == -1):
                    self.USB_PORT = port
                    match = port
                    break
            except (OSError, serial.SerialException):
                pass
        return match

    def connect(self):
        """Connect to the USB for the hottop.

        Attempt to discover the USB port used for the Hottop and then form a
        connection using the serial library.

        :returns: bool
        :raises SerialConnectionError:
        """
        match = self._autodiscover_usb()
        self._log.debug("Auto-discovered USB port: %s" % match)
        try:
            self._conn = serial.Serial(self.USB_PORT, baudrate=self.BAUDRATE,
                                       bytesize=self.BYTE_SIZE,
                                       parity=self.PARITY,
                                       stopbits=self.STOPBITS,
                                       timeout=self.TIMEOUT)
        except serial.serialutil.SerialException as e:
            raise SerialConnectionError(str(e))

        self._log.debug("Serial connection set")
        if not self._conn.isOpen():
            self._conn.open()
            self._log.debug("Serial connection opened")
        return True

    def _init_controls(self):
        """Establish a set of base controls the user can influence.

        :returns: None
        """
        self._config['heater'] = 0
        self._config['fan'] = 0
        self._config['main_fan'] = 0
        self._config['drum_motor'] = 0
        self._config['solenoid'] = 0
        self._config['cooling_motor'] = 0
        self._config['interval'] = self.INTERVAL
        self._config['external_temp'] = 0
        self._config['bean_temp'] = 0
        self._config['chaff_tray'] = 1

    def _callback(self, data):
        """Processor callback to clean-up stream data.

        This function provides a hook into the output stream of data from the
        controller processing thread. Hottop readings are saved into a local
        class variable for later saving. If the user has defined a callback, it
        will be called within this private function.

        :param data: Information from the controller process
        :type data: dict
        :returns: None
        """
        if not self._roast_start:
            return
        td = (now_time() - self._roast_start)
        data['time'] = (td.total_seconds() + 60) / 60  # Seconds since starting
        self._log.debug(data)
        self._roast.append(data)
        if self._user_callback:
            self._log.debug("Passing data back to client handler")
            self._user_callback(data)

    def start(self, func=None):
        """Start the roaster control process.

        This function will kick off the processing thread for the Hottop and
        register any user-defined callback function.

        :param func: Callback function for Hottop stream data
        :type func: function
        :returns: None
        """
        self._user_callback = func
        self._process = ControlProcess(self._conn, self._config, self._q,
                                       self._log, callback=self._callback)
        self._roast_start = now_time()
        self._process.start()
        self._roasting = True

    def end(self):
        """End the roaster control process via thread signal.

        :returns: None
        """
        self._process.shutdown()
        self._roasting = False
        self._roast_end = now_time()

    def drop(self):
        """Preset call to drop coffee from the roaster via thread signal.

        :returns: None
        """
        self._process.drop()

    def get_serial_state(self):
        """Get the state of the USB connection.

        :returns: dict
        """
        if not self._conn:
            return False
        return self._conn.isOpen()

    def get_current_config(self):
        """Get the current running config and state.

        :returns: dict
        """
        return {
            'state': self.get_serial_state(),
            'settings': dict(self._config)
        }

    def set_interval(self, interval):
        """Set the polling interval for the process thread.

        :param interval: How often to poll the Hottop
        :type interval: int or float
        :returns: None
        :raises: InvalidInput
        """
        if type(interval) != float or type(interval) != int:
            raise InvalidInput("Interval value must be of float or int")
        self._config['interval']

    def get_heater(self):
        """Get the heater config.

        :returns: int [0-100]
        """
        return self._config['heater']

    def set_heater(self, heater):
        """Set the heater config.

        :param heater: Value to set the heater
        :type heater: int [0-100]
        :returns: None
        :raises: InvalidInput
        """
        if type(heater) != int and heater not in range(0, 101):
            raise InvalidInput("Heater value must be int between 0-100")
        self._config['heater'] = heater
        self._q.put(self._config)

    def get_fan(self):
        """Get the fan config.

        :returns: int [0-10]
        """
        return self._config['fan']

    def set_fan(self, fan):
        """Set the fan config.

        :param fan: Value to set the fan
        :type fan: int [0-10]
        :returns: None
        :raises: InvalidInput
        """
        if type(fan) != int and fan not in range(0, 11):
            raise InvalidInput("Fan value must be int between 0-10")
        self._config['fan'] = fan
        self._q.put(self._config)

    def get_main_fan(self):
        """Get the main fan config.

        :returns: None
        """
        return self._config['main_fan']

    def set_main_fan(self, main_fan):
        """Set the main fan config.

        :param main_fan: Value to set the main fan
        :type main_fan: int [0-10]
        :returns: None
        :raises: InvalidInput
        """
        if type(main_fan) != int and main_fan not in range(0, 11):
            raise InvalidInput("Main fan value must be int between 0-10")
        self._config['main_fan'] = main_fan
        self._q.put(self._config)

    def get_drum_motor(self):
        """Get the drum motor config.

        :returns: None
        """
        return self._config['drum_motor']

    def set_drum_motor(self, drum_motor):
        """Set the drum motor config.

        :param drum_motor: Value to set the drum motor
        :type drum_motor: bool
        :returns: None
        :raises: InvalidInput
        """
        if type(drum_motor) != bool:
            raise InvalidInput("Drum motor value must be bool")
        self._config['drum_motor'] = bool2int(drum_motor)
        self._log.debug(self._config)
        self._q.put(self._config)

    def get_solenoid(self):
        """Get the solenoid config.

        :returns: None
        """
        return self._config['solenoid']

    def set_solenoid(self, solenoid):
        """Set the solenoid config.

        :param solenoid: Value to set the solenoid
        :type solenoid: bool
        :returns: None
        :raises: InvalidInput
        """
        if type(solenoid) != bool:
            raise InvalidInput("Solenoid value must be bool")
        self._config['solenoid'] = bool2int(solenoid)
        self._q.put(self._config)

    def get_cooling_motor(self):
        """Get the cooling motor config.

        :returns: None
        """
        return self._config['cooling_motor']

    def set_cooling_motor(self, cooling_motor):
        """Set the cooling motor config.

        :param cooling_motor: Value to set the cooling motor
        :type cooling_motor: bool
        :returns: None
        :raises: InvalidInput
        """
        if type(cooling_motor) != bool:
            raise InvalidInput("Cooling motor value must be bool")
        self._config['cooling_motor'] = bool2int(cooling_motor)
        self._q.put(self._config)
