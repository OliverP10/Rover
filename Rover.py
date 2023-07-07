import logging
from Movement import Movement
from PwmController import PwmController
from SocketLoggingHandler import SocketLoggingHandler
from Arm import Arm
from Camera import Camera
from Communicaition import Communicaition
from Sensors import Sensors

from typing import List
import RPi.GPIO as GPIO
import json
import time


class Rover:
    logger: any
    start_time: float
    communication: Communicaition
    camera: Camera
    sensors: Sensors
    #pwm_controller: PwmController
    movement: Movement
    arm: Arm
    control_mappings: dict

    def __init__(self) -> None:
        self.start_time = time.time()
        self.start()

    def start(self) -> None:
        self.logger = logging.getLogger("Rover")
        self.logger.info("Rover starting up...")
        GPIO.setmode(GPIO.BCM) # Use GPI numbers for pins
        self.communication = Communicaition(self)
        self.communication.setup()
        self.setup_telem_logging()

        #self.camera = Camera()
        self.pwm_controller = PwmController()
        self.arm = Arm(self)
        self.movement = Movement(self)
        self.sensors = Sensors(self)
        self.sensors.setup()

        self.control_mappings = dict()
        self.key_mappings = dict()
        self.load_control_mappings()
        self.load_key_mappings()
        self.send_all_telem()
        self.logger.info("Rover start up complete")

    def setup_telem_logging(self):
        socketLoggingHandler = SocketLoggingHandler(self)
        socketLoggingHandler.setLevel(logging.INFO)
        socketLoggingHandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
        logging.getLogger().addHandler(socketLoggingHandler)

    def decode_control_frame(self, instuctions: json) -> None:
        for key in instuctions:
            if (key in self.control_mappings):
                self.control_mappings[key](instuctions[key])
            else:
                self.logger.debug("Instruction '"+key+"' not found")

    def load_control_mappings(self) -> None:
        self.control_mappings['13'] = self.sensors.sensor_monitoring.set_enabled
        self.control_mappings['12'] = self.decode_key_frame_up
        self.control_mappings['11'] = self.decode_key_frame_down
        self.control_mappings['10'] = self.arm.yaw.set_angle                                    # arm yaw
        self.control_mappings['9'] = self.arm.pitch1.set_angle                                  # arm pitch 1
        self.control_mappings['8'] = self.arm.pitch2.set_angle                                  # arm pitch 2
        self.control_mappings['7'] = self.arm.roll.set_angle                                    # arm roll
        self.control_mappings['6'] = self.arm.execute_sequence                                  # arm sequence
        self.control_mappings['5'] = self.arm.set_enabled                                       # arm armed
        self.control_mappings['4'] = self.arm.set_manual_override                               # arm override
        self.control_mappings['3'] = self.arm.claw.set_enabled                                  # claw armed
        self.control_mappings['2'] = self.movement.set_enabled                                  # movement armed
        self.control_mappings['1'] = self.movement.set_speed                                    # movement speed
        self.control_mappings['0'] = self.communication.radio_communication.setRadioConnected   # radio connected

    def decode_key_frame_up(self, char: int) -> None:
        if chr(char)+"_u" in self.key_mappings:
            self.key_mappings[chr(char)+"_u"]()
        else:
            self.logger.debug(("key '"+chr(char)+"_u"+"' not found"))

    def decode_key_frame_down(self, char: int) -> None:
        if chr(char)+"_d" in self.key_mappings:
            self.key_mappings[chr(char)+"_d"]()
        else:
            self.logger.debug(("key '"+chr(char)+"_d"+"' not found"))

    def load_key_mappings(self) -> None:
        self.key_mappings["u_d"] = self.arm.yaw.increase_angle
        self.key_mappings["j_d"] = self.arm.yaw.decrease_angle
        self.key_mappings["i_d"] = self.arm.pitch1.increase_angle
        self.key_mappings["k_d"] = self.arm.pitch1.decrease_angle
        self.key_mappings["o_d"] = self.arm.pitch2.increase_angle
        self.key_mappings["l_d"] = self.arm.pitch2.decrease_angle
        self.key_mappings["p_d"] = self.arm.roll.increase_angle
        self.key_mappings[";_d"] = self.arm.roll.decrease_angle

        self.key_mappings["[_d"] = self.arm.claw.open
        self.key_mappings["[_u"] = self.arm.claw.stop
        self.key_mappings["'_d"] = self.arm.claw.close
        self.key_mappings["'_u"] = self.arm.claw.stop

        self.key_mappings["q_d"] = self.movement.left_forward
        self.key_mappings["q_u"] = self.movement.left_stop
        self.key_mappings["a_d"] = self.movement.left_backward
        self.key_mappings["a_u"] = self.movement.left_stop
        self.key_mappings["e_d"] = self.movement.right_forward
        self.key_mappings["e_u"] = self.movement.right_stop
        self.key_mappings["d_d"] = self.movement.right_backward
        self.key_mappings["d_u"] = self.movement.right_stop

        self.key_mappings["w_d"] = self.movement.all_forward
        self.key_mappings["w_u"] = self.movement.all_stop
        self.key_mappings["s_d"] = self.movement.all_backward
        self.key_mappings["s_u"] = self.movement.all_stop

    def send_all_telem(self):
        self.movement.send_all_telem()
        self.arm.send_all_telem()
