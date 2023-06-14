import threading
import time
from sensors import Compass, GPS
import cv2
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import  QApplication, QWidget, QLabel, QPushButton
from statistics import mean
from plot import pyPlot
import datetime as dt
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import median_filter
from filters import Filter
import time
import os
import sys
import imufusion

class Manager(Compass, GPS):
    def __init__(self, ser) -> None:
        super(Manager, self).__init__()
        self.ser = ser
        self.get_command = "$fcew\r\n".encode("utf-8")
        self.my_bearing = 0
        self.acc = 0
        self.myCoors =  [37.93349, 23.87531]
        self.tarCoors = [37.93345, 23.87479]
        self.screen_res = [640, 480]
        self.fov = 31.5
        self.plot = pyPlot()
        self.filterX=Filter(4)     
        self.filterY=Filter(8)  
        self.filterZ=Filter(4)  
        self.px_per_deg = 20.3
        self.px_dg_y = 16
        self.magnetic_declination = 5.04
        # self.app = QApplication(sys.argv)
        # self.viewer = ImageWidget()
        # self.timer = QTimer()
        # self.createUI()
        self.cap = cv2.VideoCapture(0)
        self.target_size = 30 # Pixels
        #threading.Thread(target=self.read_compass, args=()).start()
        self.th_stop_f = False
        self.yaw_temp = 0
        self.init_fl = False
        self.yaw_ahrs = 0
        self.pitch_ahrs = 0
        threading.Thread(target=self.ahrs_heading, args=()).start()

        self.softItonMtx = [[1.039, -0.002, 0.029],[-0.002, 1.044, 0.027],[0.029, 0.027, 0.924]]
        self.hardIronMtx = [-16.03, -6.11, -17.86]
        

    def createUI(self):
        self.viewer.setWindowTitle("eCompass")
        self.viewer.resize(600, 600)        
        self.viewer.label = QLabel(self.viewer)
        self.viewer.label.setGeometry(200, 100, 400, 300)
        self.viewer.label.move(200,100)
        self.viewer.label.setFont(QFont('Arial', 28))
        self.viewer.keyPressed.connect(self.on_key)


    def exec(self):
        self.init_angle()
        self.timer.timeout.connect(self.calc_angle)
        self.timer.start(20)
        self.viewer.show()
        self.app.exec_()

    def set_myCoors(self, lat, long):
        self.myCoors = lat, long

    def on_key(self, key):
        if key == Qt.Key_Escape:
            os._exit(1)
        elif key == Qt.Key_R:
            self.init_angle()

    def set_tarCoors(self, lat, long):
        self.tarCoors = lat, long

    def set_true_bearing(self, bearing):
        self.my_bearing = bearing#  + self.magnetic_declination

    def init_angle(self):
        print("reset")
        self.init_fl = True

    
    def ahrs_heading(self):
        # heading = np.empty((500, 3))
        # head = []
        # time_a = []
        offset = imufusion.Offset(32)  #100Hz Sample Rate
        ahrs = imufusion.Ahrs()
        # print(help(offset))
        ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   14,  # acceleration rejection
                                   30,  # magnetic rejection
                                   5 * 32)  # rejection timeout = 5 seconds
        st = time.time()
        # for i in range(2000):
        while 1:
            try:
                mes = self.ser.read_serial()
                mes = mes.decode("utf-8")
                val = mes.split(",")
                gyroscope = val[0:3]
                accelerometer = val[3:6]
                magnetometer = val[6:9]
                gyroscope = np.array([int(i)/131.1 for i in gyroscope]) * [1, 1, -1]
                accelerometer = np.array([int(i)/16384 for i in accelerometer]) * [1, 1, -1]
                magnetometer = np.array([int(i) * 0.10 for i in magnetometer])
                gyroscope = offset.update(gyroscope)
                magnetometer = np.subtract(magnetometer, self.hardIronMtx)
                # interval = time.time()-st
                # print(interval)
                ahrs.update(gyroscope, accelerometer, magnetometer, 1/32)
                # st = time.time()
                # ahrs.update_no_magnetometer(gyroscope, accelerometer, 1/32)
                roll,pitch,yaw = ahrs.quaternion.to_euler()
                if pitch <0:
                    self.pitch_ahrs = pitch + 360
                else:
                    self.pitch_ahrs = pitch
                if yaw <0:
                    self.yaw_ahrs = yaw + 360
                else:
                    self.yaw_ahrs = yaw
                print(self.yaw_ahrs)
                # print(self.yaw_ahrs, self.pitch_ahrs)
                # if i>500:
                #     head.append(yaw)
                #     time_a.append(time.time()-st)
            except Exception as e:
                print(f"Error: {str(e)}")
        # self.plot.ax1.plot(time_a, head)
        # print((max(head) - min(head))/2)
        # plt.show()



    def calc_angle(self):
        mes = self.ser.read_serial()
        mes = mes.decode("utf-8")
        if "Mag" in mes:
            self.get_values_from_serial(mes, "MGN")
        elif "Acc" in mes:
            self.get_values_from_serial(mes, "ACC")
        # if "Yaw" in mes:
        #     val = float(mes.split("=")[1])
        try:
            self.angle_from_magn()

            yaw = int(self.filterX.moving_average(self.yaw))
            #yaw = int(self.yaw)
            # if self.init_fl is True:
            #     self.yaw_temp = yaw
            #     self.init_fl = False     
            self.viewer.label.setText(str(yaw))               
        except Exception as e:
            pass

    def export(self):
        with open("C:\\Users\\dkalaitzakis\\Desktop\\compass_log.txt", "w") as f:
            for i in range(1000):
                mes = self.ser.read_serial()
                mes = mes.decode("utf-8")
                if "Mgn" in mes:
                    self.get_values_from_serial(mes,"MGN")
                    x,y,z = self.get_magn_values()
                elif "Acc" in mes:
                    self.get_values_from_serial(mes,"ACC")
                    ax,ay,az = self.get_acc_values()
                try:
                    st = f"{ax} {ay} {az} {x} {y} {z}"
                    f.write(st)
                    f.write("\n")
                except Exception as e:
                    print(str(e))


    def plot_from_file(self):
        f = []
        head = []
        time = []
        with open("C:\\Users\\dkalaitzakis\\Documents\\1074701_2023-04-02_09_45_19.csv", "+r") as file:
            f =file.readlines()
        for i in f:
            temp = i.split(",")
            h = temp[1].strip("\n")
            head.append(float(h))
            time.append(int(temp[0]))

        self.plot.ax1.plot(time, head)
        print(max(head) - min(head))
        plt.show()
        os._exit(-1)


    def port_to_file(self):
        with open("C:\\Users\\dkalaitzakis\\Documents\\ahrs_input.csv", "a") as file:
            st = time.time()
            file.write("\n")
            for i in range(500):
                try:
                    mes = self.ser.read_serial()
                    mes = mes.decode("utf-8")
                    val = mes.split(",")
                except:
                    pass
                for i in range(0,len(val)):
                    if i in range(0,3):
                        val[i] = str(int(val[i]) / 500)
                    elif i in range(3,6):
                        val[i] = str(int(val[i]) / 1000)
                    elif i in range(6,9):
                        val[i] = str(int(val[i]) * 1.5)
                val.insert(0,str(time.time()-st))
                val = ",".join(val)
                print(val)
                file.write(val+"\n")
                




    def plot_3d_magn(self):
        gx=[]
        gy=[]
        gz=[]
        st = time.time()
        mx = None
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        for i in range(1500):
            try:
                mes = self.ser.read_serial()
                mes = mes.decode("utf-8")
                if "Mgn" in mes:
                    self.get_values_from_serial1(mes)
                    x,y,z = self.get_magn_values()
                    mx = self.filterX.moving_average(x)
                    my = self.filterY.moving_average(y)
                    mz = self.filterZ.moving_average(z)
                if mx is not None:
                    gx.append(mx)
                    gy.append(my)
                    gz.append(mz)
            except Exception as e:
                print(f"Serial parching error: {str(e)}")
        ax.scatter(gx,gy,gz)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()


    def read_magn_row(self):
        bx=[]
        by=[]
        bz=[]
        gx=[]
        gy=[]
        gz=[]
        tb=[]
        tg=[]
        st = time.time()
        for i in range(3000):
            try:
                mes = self.ser.read_serial()
                mes = mes.decode("utf-8")
            
                if "Mgn" in mes:
                    self.get_values_from_serial(mes,"MGN")
                    x,y,z = self.get_magn_values()
                    ax = self.filterX.moving_average(x)
                    ay = self.filterY.moving_average(y)
                    az = self.filterZ.moving_average(z)
                    print(ax)
                if i > 50:
                    bx.append(x)
                    by.append(y)
                    bz.append(z)
                    tb.append(time.time()-st)
                # elif "Acc" in mes:
                #     self.get_values_from_serial(mes,"ACC")
                #     ax,ay,az = self.get_acc_values()
                    gx.append(ax)
                    gy.append(ay)
                    gz.append(az)
                    # tg.append(time.time()-st)
            except Exception as e:
                print(f"Serial parching error: {str(e)}")
            self.plot.ax1.plot(tb, bx)
            self.plot.ax1.grid()
            self.plot.ax2.plot(tb, by)
            self.plot.ax2.grid()
            self.plot.ax3.plot(tb, bz)
            self.plot.ax3.grid()
            self.plot.ax4.plot(tb, gx)
            self.plot.ax4.grid()
            self.plot.ax5.plot(tb, gy)
            self.plot.ax5.grid()
            self.plot.ax6.plot(tb, gz)
            self.plot.ax6.grid()
        print((max(gx) - min(gx))/2)
        print((max(gy) - min(gy))/2)
        print((max(gz) - min(gz))/2)
        print(time.time()-st)
        plt.show()
        os._exit(-1)


    def calc_angle_from_raw(self):
        yaw_b = []
        yaw_c = []
        tb=[]
        st = time.time()
        for i in range(1000):
            try:
                mes = self.ser.read_serial()
                mes = mes.decode("utf-8")
                self.get_values_from_serial1(mes)
                try:
                    self.angle_from_magn()
                    if self.yaw != 0:
                        yaw = self.filterX.IIR_filter_ch2(self.yaw)   
                        yaw = self.filterY.moving_average(yaw)
                        print("Yaw", yaw)
                        
                        if i>30:          
                            # if yaw is not None:
                            yaw_b.append(yaw)
                            yaw_c.append(self.yaw)
                        # yaw_d.append(val)     
                            tb.append(time.time()-st)
                            self.plot.ax1.plot(tb, yaw_b)
                            self.plot.ax2.plot(tb, yaw_c)   
                    # self.plot.ax3.plot(tb, yaw_c) 
                except Exception as e:
                    print(str(e))
            except Exception as e:
                    print(str(e))
            #print("magn:", self.get_magn_values())
        print(time.time()-st)
        print(max(yaw_b) - min(yaw_b))
        print(max(yaw_c) - min(yaw_c))
        plt.show()
        os._exit(-1)


    # def show(self):
    #     self.st = time.time()
    #     ani = FuncAnimation(self.plot.fig, self.read_compass, interval= 100)
    #     self.plot.format_plot()
    #     self.plot.set_title("eCompass Raw LSB Median_12")
    #     plt.show()

    def send_get_command(self):
        while 1:
            if self.th_stop_f is False:
                self.ser.write_serial(self.get_command)
                time.sleep(0.02)


    def get_lines(self, coors):
        l1 = [[coors[0],coors[1]-int(self.target_size/2)], [coors[0]-int(self.target_size/2),coors[1]+int(self.target_size/2)]]
        l2 = [[coors[0],coors[1]-int(self.target_size/2)], [coors[0]+int(self.target_size/2),coors[1]+int(self.target_size/2)]]
        l3 = [[coors[0]-int(self.target_size/2),coors[1]+int(self.target_size/2)], [coors[0]+int(self.target_size/2),coors[1]+int(self.target_size/2)]]
        return l1,l2,l3
    
    def project(self):
        while 1:
            ret,frame = self.cap.read()
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            angle = self.calculate_angle()
            if angle > 0 and angle < self.fov:
                tar_center_pxl = int(angle * self.px_per_deg)
                if self.pitch_ahrs > 180:
                    tar_y = int((self.pitch_ahrs - 345) * self.px_dg_y) 
                else:
                    tar_y = int((self.pitch_ahrs + 15) * self.px_dg_y) 
                l1,l2,l3 = self.get_lines([tar_center_pxl, tar_y])
                cv2.line(frame, l1[0], l1[1], (0,255,255), 1)
                cv2.line(frame, l2[0], l2[1], (0,255,255), 1)
                cv2.line(frame, l3[0], l3[1], (0,255,255), 1)
            elif angle < 0:
                cv2.line(frame, (0,240), (30,210), (0,255,255) ,1)
                cv2.line(frame, (0,240), (30,270), (0,255,255) ,1)
            elif angle > self.fov:
                cv2.line(frame, (610,210), (640,240), (0,255,255) ,1)
                cv2.line(frame, (610,270), (640,240), (0,255,255) ,1)
            cv2.imshow("test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        os._exit(-1)

    def calculate_angle(self):
        angle = self.get_bearing(self.myCoors[0], self.myCoors[1], self.tarCoors[0], self.tarCoors[1]) + self.yaw_ahrs + (self.fov/2)
        if angle > 360:
            angle -= 360
        return angle




class ImageWidget(QWidget):
    keyPressed = pyqtSignal(int)

    def keyPressEvent(self, event):
        super(ImageWidget, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())



    

    