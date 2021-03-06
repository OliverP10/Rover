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
    pwm_controller: PwmController
    movement:Movement
    arm: Arm
    control_mappings: dict
    
    def __init__(self) -> None:
        self.start_time = time.time()
        self.start()

    def start(self) -> None:
        self.logger = logging.getLogger("Rover")
        self.logger.info("Rover starting up...")
        self.communication = Communicaition(self)
        self.setup_telem_logging()
        
        self.camera = Camera()
        self.pwm_controller = PwmController()
        self.movement = Movement(self)
        self.arm = Arm(self)
        #self.sensors = Sensors(self)
        
        self.control_mappings = dict()
        self.key_mappings = dict()
        self.load_control_mappings()
        self.load_key_mappings()
        self.logger.info("Rover start up complete")

    def setup_telem_logging(self):
        socketLoggingHandler = SocketLoggingHandler(self)
        socketLoggingHandler.setLevel(logging.INFO)
        socketLoggingHandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
        logging.getLogger().addHandler(socketLoggingHandler)

    def decode_control_frame(self, instuctions:json) -> None:
        for key in instuctions:
            if(key in self.control_mappings):
                self.control_mappings[key](instuctions[key])
            else:
                self.logger.debug("Instruction '"+key+"' not found")

    def load_control_mappings(self) -> None:
        self.control_mappings['arm_yaw'] = self.arm.yaw.set_angle
        self.control_mappings['arm_pitch1'] = self.arm.pitch1.set_angle
        self.control_mappings['arm_pitch2'] = self.arm.pitch2.set_angle
        self.control_mappings['arm_sequence'] = self.arm.execute_sequence
        self.control_mappings['arm_armed'] = self.arm.set_enabled
        self.control_mappings['movement_armed'] = self.movement.set_enabled
        self.control_mappings['movement_speed'] = self.movement.set_speed

    def decode_key_frame(self, key:str) -> None:
        if(key in self.key_mappings):
            self.key_mappings[key]()
        else:
            self.logger.debug("Keybinding '"+key+"' not found")

    def load_key_mappings(self) -> None:    #have to re do this when i re write the servo class anyway  # idead, have a run method for each class and then just ahve the one thread loop thoruhg all the run methods every x millis
        self.key_mappings['j_d'] = self.arm.yaw.increase_angle
        self.key_mappings['u_d'] = self.arm.yaw.decrease_angle
        self.key_mappings['i_d'] = self.arm.pitch1.increase_angle
        self.key_mappings['k_d'] = self.arm.pitch1.decrease_angle
        self.key_mappings['o_d'] = self.arm.pitch2.increase_angle
        self.key_mappings['l_d'] = self.arm.pitch2.decrease_angle

        self.key_mappings['q_d'] = self.movement.left_forward
        self.key_mappings['q_u'] = self.movement.left_stop
        self.key_mappings['a_d'] = self.movement.left_backward
        self.key_mappings['a_u'] = self.movement.left_stop
        self.key_mappings['e_d'] = self.movement.right_forward
        self.key_mappings['e_u'] = self.movement.right_stop
        self.key_mappings['d_d'] = self.movement.right_backward
        self.key_mappings['d_u'] = self.movement.right_stop

        self.key_mappings['w_d'] = self.movement.all_forward
        self.key_mappings['w_u'] = self.movement.all_stop
        self.key_mappings['s_d'] = self.movement.all_backward
        self.key_mappings['s_u'] = self.movement.all_stop


       
