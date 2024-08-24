import time
import math
import smbus
# import sshkeyboard

# Raspi PCA9685 16-Channel PWM Servo Driver
# Registers/etc.
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
MODE1              = 0x00
MODE2              = 0x01
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALLLED_ON_L        = 0xFA
ALLLED_ON_H        = 0xFB
ALLLED_OFF_L       = 0xFC
ALLLED_OFF_H       = 0xFD
  
SERVO_MOTOR_PWM3        = 6
SERVO_MOTOR_PWM4        = 7
SERVO_MOTOR_PWM5        = 8
SERVO_MOTOR_PWM6        = 9
SERVO_MOTOR_PWM7        = 10
SERVO_MOTOR_PWM8        = 11

DC_MOTOR_PWM1        = 0
DC_MOTOR_INA1        = 2
DC_MOTOR_INA2        = 1

DC_MOTOR_PWM2        = 5
DC_MOTOR_INB1        = 3
DC_MOTOR_INB2        = 4

class PCA9685:
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        self.dev_addr = 0x7f
        self.write_reg(MODE1, 0x00)

    def write_reg(self, reg, value):
        self.i2c.write_byte_data(self.dev_addr, reg, value)

    def read_reg(self, reg):
        res = self.i2c.read_byte_data(self.dev_addr, reg)
        return res

    def setPWMFreq(self, freq):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.read_reg(MODE1)
        print('lodmode:',oldmode)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write_reg(MODE1, newmode)        # go to sleep
        self.write_reg(PRESCALE, int(math.floor(prescale)))
        self.write_reg(MODE1, oldmode)
        time.sleep(0.005)
        self.write_reg(MODE1, oldmode | 0x80)  # 0x80

    def setPWM(self, ch, on, off):
        self.write_reg(LED0_ON_L+4*ch, on & 0xFF)
        self.write_reg(LED0_ON_H+4*ch, on >> 8)
        self.write_reg(LED0_OFF_L+4*ch, off & 0xFF)
        self.write_reg(LED0_OFF_H+4*ch, off >> 8)

    def setServoPulse(self, channel, pulse):
       pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us=20ms
       self.setPWM(channel, 0, int(pulse))


# pwm = PCA9685()
# pwm.setPWMFreq(50) # for servo


# def one_forward(motor, speed):
#     DC_MOTOR_PWM = None
#     DC_MOTOR_IN1 = 0
#     DC_MOTOR_IN2 = 0

#     if motor == 1:
#         DC_MOTOR_PWM = DC_MOTOR_PWM1
#         DC_MOTOR_IN1 = DC_MOTOR_INA1
#         DC_MOTOR_IN2 = DC_MOTOR_INA2
#     elif motor == 2:
#         DC_MOTOR_PWM = DC_MOTOR_PWM2
#         DC_MOTOR_IN1 = DC_MOTOR_INB1
#         DC_MOTOR_IN2 = DC_MOTOR_INB2
#     else:
#         raise RuntimeError
    
#     pwm.setServoPulse(DC_MOTOR_PWM, 15000)
#     pwm.setServoPulse(DC_MOTOR_IN1, 0)
#     pwm.setServoPulse(DC_MOTOR_IN2, speed)


# def one_backward(motor, speed):
#     DC_MOTOR_PWM = None
#     DC_MOTOR_IN1 = 0
#     DC_MOTOR_IN2 = 0

#     if motor == 1:
#         DC_MOTOR_PWM = DC_MOTOR_PWM1
#         DC_MOTOR_IN1 = DC_MOTOR_INA1
#         DC_MOTOR_IN2 = DC_MOTOR_INA2
#     elif motor == 2:
#         DC_MOTOR_PWM = DC_MOTOR_PWM2
#         DC_MOTOR_IN1 = DC_MOTOR_INB1
#         DC_MOTOR_IN2 = DC_MOTOR_INB2
#     else:
#         raise RuntimeError
    
#     pwm.setServoPulse(DC_MOTOR_PWM, 15000)
#     pwm.setServoPulse(DC_MOTOR_IN1, speed)
#     pwm.setServoPulse(DC_MOTOR_IN2, 0)


# def full_forward_for_time(speed, duration=1):
#     one_forward(1, speed)
#     one_forward(2, speed)
#     time.sleep(duration)
#     full_stop()


# def full_backward_for_time(speed, duration=1):
#     one_backward(1, speed)
#     one_backward(2, speed)
#     time.sleep(duration)
#     full_stop()


# def one_backward_for_time(motor, speed, duration=1):
#     one_backward(motor, speed)
#     time.sleep(duration)
#     one_stop(motor)


# def one_stop(motor):
#     DC_MOTOR_PWM = None
#     if motor == 1:
#         DC_MOTOR_PWM = DC_MOTOR_PWM1
#     elif motor == 2:
#         DC_MOTOR_PWM = DC_MOTOR_PWM2
#     else:
#         raise RuntimeError
#     pwm.setServoPulse(DC_MOTOR_PWM, 0)


# def full_stop():
#     one_stop(1)
#     one_stop(2)


# def one_forward_for_time(motor, speed, duration=1):
#     one_forward(motor, speed)
#     time.sleep(duration)
#     one_stop(motor)


# def turn_in_place_cw_for_time(duration, speed):
#     one_forward(2, speed)
#     one_backward(1, speed)
#     time.sleep(time)
#     full_stop()


# def turn_in_place_ccw_for_time(duration, speed):
#     one_forward(1, speed)
#     one_backward(2, speed)
#     time.sleep(duration)
#     full_stop()


# def set_motor_status(motor, status, speed=19000):
#     DC_MOTOR_PWM = None
#     DC_MOTOR_IN1 = 0
#     DC_MOTOR_IN2 = 0

#     if motor == 1:
#         DC_MOTOR_PWM = DC_MOTOR_PWM1
#         DC_MOTOR_IN1 = DC_MOTOR_INA1
#         DC_MOTOR_IN2 = DC_MOTOR_INA2
#     elif motor == 2:
#         DC_MOTOR_PWM = DC_MOTOR_PWM2
#         DC_MOTOR_IN1 = DC_MOTOR_INB1
#         DC_MOTOR_IN2 = DC_MOTOR_INB2
#     else:
#         raise RuntimeError
    
#     if status == 0:
#         pwm.setServoPulse(DC_MOTOR_PWM, 0)
#     elif status == 1:
#         pwm.setServoPulse(DC_MOTOR_PWM, 15000)
#         pwm.setServoPulse(DC_MOTOR_IN1, 0)
#         pwm.setServoPulse(DC_MOTOR_IN2, speed)
#     elif status == -1:
#         pwm.setServoPulse(DC_MOTOR_PWM, 15000)
#         pwm.setServoPulse(DC_MOTOR_IN1, speed)
#         pwm.setServoPulse(DC_MOTOR_IN2, 0)


# if __name__=='__main__':
    """for servo motor:
    the high part of the pulse is T
    T = 0.5ms => 0   degree
    T = 1.0ms => 45  degree
    T = 1.5ms => 90  degree
    T = 2.0ms => 135 degree
    T = 2.5ms => 180 degree
  
    for 2 channel DC motor driven by TB6612FNG
    IN1   IN2  PWM  STBY  OUT1   OUT2      MODE
    H     H   H/L   H     L      L    short brake
    L     H    H    H     L      H       CCW
    L     H    L    H     L      L    short brake
    H     L    H    H     H      L       CW
    H     L    L    H     L      L    short brake
    L     L    H    H    OFF    OFF      STOP
    H/L   H/L  H/L   L    OFF    OFF    standby
    """
    # pwm = PCA9685()
    # pwm.setPWMFreq(50) # for servo        

    # while True:
        # """The following code is applied to
        # DC motor control
        # """
        # time.sleep(2)
        # pwm.setServoPulse(DC_MOTOR_PWM1,15000) # for TB6612 set speed
        # pwm.setServoPulse(DC_MOTOR_PWM2,15000) # for TB6612 set speed
        # # CCW
        # pwm.setServoPulse(DC_MOTOR_INA1,0) # set INA1 L 
        # pwm.setServoPulse(DC_MOTOR_INA2,10000) # set INA2 H
        # pwm.setServoPulse(DC_MOTOR_INB1,0) # set INA1 L 
        # pwm.setServoPulse(DC_MOTOR_INB2,10000) # set INA2 H
        # print("M1 rotate")
        # time.sleep(2)
        # # CW
        # pwm.setServoPulse(DC_MOTOR_INA1,19999) # set INA1 H 
        # pwm.setServoPulse(DC_MOTOR_INA2,0) # set INA2 L
        # pwm.setServoPulse(DC_MOTOR_INB1,19999) # set INA1 H 
        # pwm.setServoPulse(DC_MOTOR_INB2,0) # set INA2 L
        # print("M1 rotate opposite")
        # time.sleep(2)
        # pwm.setServoPulse(DC_MOTOR_PWM1,0) # for TB6612 set speed to 0, stop        
        # pwm.setServoPulse(DC_MOTOR_PWM2,0) # for TB6612 set speed to 0, stop        

        # print("M1 stop")
        # time.sleep(2)

      
        # pwm.setServoPulse(DC_MOTOR_PWM2,15000) # for TB6612 set speed
        # # CCW
        # pwm.setServoPulse(DC_MOTOR_INB1,0) # set INB1 L 
        # pwm.setServoPulse(DC_MOTOR_INB2,19999) # set INB2 H
        # print("M2 rorate")
        # time.sleep(2)
        # # CW
        # pwm.setServoPulse(DC_MOTOR_INB1,19999) # set INB1 H 
        # pwm.setServoPulse(DC_MOTOR_INB2,0) # set INB2 L
        # print("M2 rorate opposite")
        # time.sleep(2)
        # pwm.setServoPulse(DC_MOTOR_PWM2,0) # for TB6612 set speed to 0, stop
        # print("M2 stop")
        # time.sleep(2)
        
      
        # """The following code is applied to
        #   servo motor control
        # """
        # print("servo ccw")
        # for i in range(500,2500,10):# start 500, end 2500, step is 10  
        #    pwm.setServoPulse(SERVO_MOTOR_PWM3,i)   
        #    time.sleep(0.02)    
        # print("servo cw")
        # for i in range(2500,500,-10):
        #    pwm.setServoPulse(SERVO_MOTOR_PWM3,i) 
        #    time.sleep(0.02)  