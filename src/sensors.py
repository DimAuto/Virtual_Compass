import math
import re
from statistics import mean


class GPS(object):
    def __init__(self) -> None:
        super(GPS, self).__init__()

    def get_bearing(self, myLat, myLong, tarLat, tarLong):
        tarLong = math.radians(tarLong)
        myLong = math.radians(myLong)
        tarLat = math.radians(tarLat)
        myLat = math.radians(myLat)
        y = math.sin(tarLong-myLong) * math.cos(tarLat)
        x = math.cos(myLat) * math.sin(tarLat) - math.sin(myLat)* math.cos(tarLat)*math.cos(tarLong-myLong)
        θ = math.atan2(y, x)
        bearing = (θ*180/math.pi + 360) % 360 # in degrees
        #print("bngr: ", bearing)
        return bearing

    def get_distance(self, myLat, myLong, tarLat, tarLong):
        lon1 = math.radians(myLong)
        lon2 = math.radians(tarLong)
        lat1 = math.radians(myLat)
        lat2 = math.radians(tarLat)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers.
        r = 6371

        # calculate the result
        return(c * r)


class Compass(object):
    #ECOMPASS SENSOR LSM303AGR
    def __init__(self) -> None:
        super(Compass, self).__init__()
        self.magn_x = None
        self.magn_y = None
        self.magn_z = None
        self.acc_x = None
        self.acc_y = None
        self.acc_z = None
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.buffer_len = 22
        self.x_buf = []
        self.y_buf = []
        self.z_buf = []
        self.ready_flag = False
        # self.off_x_m = -343.5
        # self.off_y_m = -483.75
        # self.off_z_m = 327.75
        # self.off_x_m = -195.75  #dev_board
        # self.off_y_m = -37.5
        # self.off_z_m = -243
        self.off_x_m = 0  # iris closed
        self.off_y_m = 0
        self.off_z_m = 0

    def get_acc_values(self):    
        return [self.acc_x, self.acc_y, self.acc_z]
    
    def get_magn_values(self):
        return [self.magn_x, self.magn_y, self.magn_z]
        
    def set_magn_values_hex(self, x, y, z):
        self.magn_x = self.twos_complement(x,16) * 1.5
        self.magn_y = self.twos_complement(y,16) * 1.5
        self.magn_z = self.twos_complement(z,16) * 1.5   
        self.magn_x = self.magn_x - self.off_x_m
        self.magn_y = self.magn_y - self.off_y_m
        self.magn_z = self.magn_z - self.off_z_m
        #self.magn_filter_raw()

    def magn_filter_raw(self):
        if len(self.x_buf) < self.buffer_len:
            self.x_buf.append(self.magn_x)
            self.y_buf.append(self.magn_y)
            self.z_buf.append(self.magn_z)
        else:
            del self.x_buf[0]
            del self.y_buf[0]
            del self.z_buf[0]
            self.x_buf.append(self.magn_x)
            self.y_buf.append(self.magn_y)
            self.z_buf.append(self.magn_z)
            self.magn_x = mean(self.x_buf)
            self.magn_y = mean(self.y_buf)
            self.magn_z = mean(self.z_buf)
            self.ready_flag=True

    def set_magn_values(self, x, y, z):
        self.magn_x = float(x)# * 1.5
        self.magn_y = float(y)# * 1.5
        self.magn_z = float(z)# * 1.5
        self.magn_x = self.magn_x -self.off_x_m
        self.magn_y = self.magn_y -self.off_y_m
        self.magn_z = self.magn_z - self.off_z_m

    def set_acc_values(self, x, y, z):
        self.acc_x = float(x)# * 0.00098
        self.acc_y = float(y)# * 0.00098
        self.acc_z = float(z)# * 0.00098

    def set_acc_values_hex(self, x, y, z):
        self.acc_x = self.twos_complement(x,16)
        self.acc_y = self.twos_complement(y,16)
        self.acc_z = self.twos_complement(z,16)
        self.acc_x = self.acc_x >> 4
        self.acc_y = self.acc_y >> 4
        self.acc_z = self.acc_z >> 4
        self.acc_x = int(self.acc_x)
        self.acc_y = int(self.acc_y)
        self.acc_z = int(self.acc_z)
        # self.acc_x = self.acc_x & 0xFF
        # self.acc_y = self.acc_y & 0xFF
        # self.acc_z = self.acc_z & 0xFF

    def twos_complement(self, hexstr, bits):
        value = int(hexstr, 16)
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value
    
    def get_values_from_serial1(self, mess):
        l = []
        temp = mess.split(":")[1]
        l = temp.split("|")
        x = int(l[0])
        y = int(l[1])
        z = int(l[2])
        if "Mgn" in mess:
            self.set_magn_values(x, y, z)
        else:
            self.set_acc_values(x, y, z)


    
    def get_values_from_serial(self, mess, hw):
        l = []
        l = re.split(",|\n|=", mess)
        for i in range(0, len(l)):

            if "X" in l[i]:
                x = l[i+1]
            elif "Y" in l[i]:
                y = l[i+1]
            elif "Z" in l[i]:
                z = l[i+1]
        if hw == "MGN":
            if "x" in x:
                self.set_magn_values_hex(x, y, z)
            else:
                self.set_magn_values(x, y, z)
        else:
            if "x" in x:
                self.set_acc_values_hex(x, y, z) 
            else:
                self.set_acc_values(x, y, z)

    def angle_from_magn(self):
        # if self.ready_flag is False:
        #     self.yaw = 0
        #     return
        phi = math.atan2(self.acc_y, self.acc_z)
        self.roll = phi*(180/math.pi)
        theta=math.atan2(-self.acc_x, (self.acc_y*(math.sin(phi)) + self.acc_z*(math.cos(phi))))
        self.pitch = theta*(180/math.pi)

        bx_derot = self.magn_x*(math.cos(theta)) + (self.magn_y*(math.sin(phi))+ self.magn_z*(math.cos(phi)))* math.sin(theta) 
        by_derot = self.magn_y*(math.cos(phi)) - self.magn_z *(math.sin(phi))

        psi=math.atan2(-by_derot, bx_derot)
        self.yaw = psi * (180/math.pi)
        if self.yaw <0:
            self.yaw += 360


    def calc_heading(self):
        self.yaw = math.atan2(self.magn_y, self.magn_x) * 180/math.pi
        if self.yaw <0:
            self.yaw += 360




# c = Compass()
# c.get_values_from_serial("Magnetometer:X=-0.004, Y=0.137, Z=0.172")
# print(c.get_magn_values())
# print(c.angle_from_magn())


