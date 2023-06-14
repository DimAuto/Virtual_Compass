from serial_comm import SerialComm
from manager import Manager
import time
import os

if __name__ == "__main__":
    ser = SerialComm("34E1986E1F000D00", 115200, "\r\n") #iris_bare
    # ser = SerialComm("FT6VJEM1A", 115200, "\r\n") #msp dev
    #ser = SerialComm("A100VKF5A", 115200, "\r\n") # iris_assembled
    
    if ser.ser == None:
        ser.__del__()

    time.sleep(2)
    projector = Manager(ser)
    try:
        projector.project()
    except Exception as e:
        print(str(e))
        os._exit(-1)
    finally:
        os._exit(-1)