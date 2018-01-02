import time                                  #import the time module
import piplates.MOTORplate as MOTOR          #import the MOTORplate module

MOTOR.stepperCONFIG(0,'a','cw','M8',100,2)  #configure stepper A
MOTOR.stepperMOVE(0,'a',1600)                #Start a MOVE of 1600 steps