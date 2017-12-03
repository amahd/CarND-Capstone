#!/usr/bin/env python

import rospy
#from lowpass import LowPassFilter
from pid import PID

GAS_DENSITY = 2.858
ONE_MPH = 0.44704

PRINT_DEBUG = False # Print rospy.logwarn for debugging if True

class TwistController(object):  
    def __init__(
        self,
        vehicle_mass,
        fuel_capacity,
        brake_deadband,
        decel_limit,
        accel_limit,
        wheel_radius,
        wheel_base,
        steer_ratio,
        max_lat_accel,
        max_steer_angle):
         
        self.vehicle_mass = vehicle_mass
        self.fuel_capacity = fuel_capacity
        self.brake_deadband = brake_deadband
        self.decel_limit = decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius
        self.wheel_base = wheel_base
        self.steer_ratio = steer_ratio
        self.max_lat_accel = max_lat_accel
        self.max_steer_angle = max_steer_angle
        
        # TODO: tune parameters for PIDs and low pass filters
        
        # Using separate PIDs for throttle and brake so that their parameters
        # can be tuned separately.
        
        # Output of throttle-PID covers acceleration in range of 0..1 m/s^2
        # test_dbw.py adaption: throttle-PID covers acceleration from 0% to 2.5%
        self.throttle_pid = PID(0.35, 0.01, 0.0,    # p, i, d
                                #0.0, self.accel_limit)          
                                0.0, 0.25)         # min, max
        #self.throttle_low_pass = LowPassFilter(0.2, .1)

        # Output of brake-PID covers deceleration in range of 0..-5 m/s^2
        # test_dbw.py adaption: Output of brake-PID covers range from 10% to 25%
        # where 10% is the deadband of brake
        self.brake_pid = PID(0.35, 0.01, 0.0,           # p, i, d
                             #0.0, -self.decel_limit)
                             0.1, 0.25)                 # min, max
        #self.brake_low_pass = LowPassFilter(0.2, .1)
        
        
    # Function for controlling speed
    def control(self, v_current, v_target, elapsed_time):
        # Calculate the error
        v_error = v_target - v_current
        
        throttle = 0.
        brake = 0.

        # Decide if acceleration or deceleration is needed to get to target speed
        if v_error < 0.0:
            # Brake
            self.throttle_pid.reset()
            brake = self.brake_pid.step(-v_error, elapsed_time)
            if PRINT_DEBUG:
                rospy.logwarn('BRAKING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        else :
            # Speed up
            self.brake_pid.reset()
            throttle = self.throttle_pid.step(v_error, elapsed_time)
            if PRINT_DEBUG:
                rospy.logwarn('SPEEDING UP_________________________________')
        
        if PRINT_DEBUG:    
            rospy.logwarn('Control Info: v_error=%.3f, throttle=%.3f, brake=%.3f', v_error, throttle, brake)
        
        return throttle, brake
    
    # Function to reset the controllers
    def reset(self):
        self.throttle_pid.reset()
        self.brake_pid.reset()
