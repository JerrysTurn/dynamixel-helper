#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# base_dir = os.path.dirname(os.path.abspath(__file__))
activate_this = os.path.expanduser(
    '~/virtualenv/dxlhelper_py2test/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# The Official Dynamixel SDK Manual is here.
# http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/api_reference/python/python_porthandler/#python

import json
import constant
import dynamixel_sdk as dxlsdk
from dxl_motor import DxlMotor
from byteify import byteify
# from .dxl_motor import DxlMotor
# from .byteify import byteify


class DxlHelper(object):
    """

    TODO:
        check alias when empty in json. Is None value correctly inside?
    """

    def __init__(self, preset_file, verbosity='minimal'):
        """Inits

        Raises:
            df
        """
        # Verbose
        constant.assert_verbosity(verbosity)
        self.verbosity = constant.verbose_level[verbosity]

        # Load preset
        with open(preset_file, 'r') as f:
            preset = json.load(f, object_hook=byteify)

        ############################################
        #              Port Handlers
        ############################################
        # The 'PortHandler' requires 'device name' for initialization.
        # And the device name is different for each OS.
        #     windows: "COM1"
        #     linux: "/dev/ttyUSB0"
        #     mac: "/dev/tty.usbserial-*"

        # e.g.
        # {
        #     "/dev/ttyUSB0": {
        #         "handler": PortHandler,
        #         "baud rate": None
        # }
        self.port_handlers = {}

        # Open port
        for name in preset['ports']:
            self.__check_type_n_dupe('port', str, name, self.port_handlers)
            port_handler = dxlsdk.PortHandler(name)
            try:
                port_handler.openPort()
            except Exception as inst:
                print("Helper: [ERROR] " + inst.__str__())
                raise inst
            else:
                self.port_handlers[name] = {'handler': port_handler,
                                            'baud rate': None}
                if self.verbosity >= constant.verbose_level['detailed']:
                    print("Helper: Succeeded to open the port: \""+name+"\"")

        ############################################
        #             Packet Handlers
        ############################################
        # The 'PacketHandler' requires 'protocol version' for initialization.
        # KEY: 'protocol version', VALUE: 'packet_handler'

        # Duplicate cleaning
        protocol_set = set(preset["protocol versions"])
        self.packet_handlers = {
            version: dxlsdk.PacketHandler(version) for version in protocol_set}

        ############################################
        #                 Motor
        ############################################

        # Motor List
        id_set = set()
        alias_set = set()
        motor_list = []
        for motor in preset['motors']:
            # ID Validation
            try:
                self.__check_type_n_dupe('motor.id', int, motor['id'], id_set)
            except KeyError:
                print("Helper: [ERROR] One motor has no ID.")
                print("        Please check again: "+preset_file)
                raise RuntimeError
            else:
                id_set.add(motor['id'])
            # Alias Validation
            try:
                if motor['alias']:
                    self.__check_type_n_dupe('motor.alias', str, motor['alias'], alias_set)
                    alias_set.add(motor['alias'])
                else:
                    motor['alias'] = None
            except KeyError:
                motor.update({'alias': None})
            # Clean list
            motor_list.append(motor)
            # {
            #     "id": 1,
            #     "alias": "joint_L1",
            #     "model": "XM430-W210"
            # }
        self.num_motors = len(motor_list)

        # KEY: 'robotID' or 'alias', VALUE: 'DxlMotor'
        self.__motors = {}
        logging = {'O': [], 'X': []}
        for motor in motor_list:
            motor_log = [motor['id'], motor['alias'], motor['model']]
            try:
                motorInstance = DxlMotor(
                    motor['id'], motor['alias'], motor['model'],
                    self.port_handlers, preset['baud rates'],
                    self.packet_handlers,
                    verbosity=verbosity)
            except:  # to catch all errors
                logging['X'].append(motor_log)
                if self.verbosity >= constant.verbose_level['detailed']:
                    print("Helper: One motor setup was skipped.")
            else:
                logging['O'].append(motor_log)
                self.__motors[motor['id']] = motorInstance
                if motor['alias']:
                    self.__motors[motor['alias']] = motorInstance
                if self.verbosity >= constant.verbose_level['detailed']:
                    print("Helper: One motor setup was completed.")
            # finally:
            #     pass
            #     motor_log.append(motorInstance.port_name)
            #     motor_log.append(motorInstance.baud)

        ############################################
        #                 Log
        ############################################

        if self.verbosity >= constant.verbose_level['minimal']:
            print("Helper: All motor setups have been completed.")
            print("        Success: {} motor(s) / Fail: {} motor(s)"
                  .format(len(logging['O']), len(logging['X'])))
            for ox, logs in logging.items():
                logs.sort()
                for log in logs:
                    print("          ({}) id:{}, alias:{}, model:{}"
                          .format(ox, log[0], log[1], log[2]))

    def __del__(self):
        """"""
        for port in self.port_handlers.values():
            port['handler'].closePort()

    @staticmethod
    def __check_type_n_dupe(name, expected_type, value, list_like):
        """
        """
        if not isinstance(value, expected_type):
            print("Helper: [ERROR] \"{}\" must be \'{}\', not \'{}\'."
                  .format(name, expected_type.__name__, type(value).__name__))
            print("        Value: {}".format(value))
            raise TypeError
        elif value in list_like:
            print("Helper: [ERROR] Duplicate {} detected. Value: {}"
                  .format(name, value))
            raise ValueError

    def get_motor(self, _id):
        """
        """
        return self.__motors[_id]


if __name__ == "__main__":

    d = DxlHelper("minimal.json", verbosity='detailed')

    def move(id_, v):
        motor = d.get_motor(id_)
        motor.set_torque(True)
        dxl_unit, _ = motor.get_present_position()
        print(motor.set_goal_position((dxl_unit + v) % 4096))

    print("--------------------")
    move(0, 500)
    print("--------------------")
    move(1, 2000)
