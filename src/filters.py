import numpy as np
from scipy.ndimage import median_filter
from statistics import mean

class Filter(object):
    def __init__(self, window_len) -> None:
        self.buffer=[0,0,0,0]
        self.counter=0
        self.window_len = window_len        
        self.fn_res = [0,0,0,0]
        self.iit_slow = [[0.00091555, 0.00061036, 0.00091555],[1, -1.92892271, 0.93136417]]
        self.iit_fast = [[0.02042691, 0.03984167, 0.02042691],[1, -1.55999967, 0.64069515]]
        self.iit_coef = self.iit_fast

    def median(self, value):
        if len(self.buffer) < self.window_len:
            self.buffer.append(value)
        else:
            del self.buffer[0]
            self.buffer.append(value)
            m = median_filter(self.buffer, size = self.window_len)
            return m[6]
        
    def moving_average(self, value):
        if len(self.buffer) < self.window_len:
            self.buffer.append(value)
        else:
            del self.buffer[0]
            self.buffer.append(value)
            m = mean(self.buffer)
            return m
        
    def IIR_filter_ch2(self, value):
        self.buffer.append(value)
        del self.buffer[0]
        num = ((self.buffer[-1] * self.iit_coef[0][0]) + (self.buffer[-2] * self.iit_coef[0][1]) + (self.buffer[-3] * self.iit_coef[0][2])) 
        fn = (num - (self.fn_res[-1] * self.iit_coef[1][1]) - (self.fn_res[-2] * self.iit_coef[1][2])) / self.iit_coef[1][0]
        self.fn_res.append(fn)
        del self.fn_res[0]
        return fn
            
    def IIR_filter_band(self, value):
        self.buffer.append(value)
        del self.buffer[0]
        num = ((self.buffer[-1] * self.iit_slow[0][0]) - (self.buffer[-2] * self.iit_slow[0][1]) - (self.buffer[-3] + self.iit_slow[0][2]) -
                (self.buffer[-4]* 0.00209581) + (self.buffer[-5] * 0.01087108)) 
        fn = (num + (2.25573502 * self.fn_res[-1]) - (self.fn_res[-2]* 2.97628384) + (self.fn_res[-3]* 1.93588914) - (self.fn_res[-4]* 0.73784076))
        self.fn_res.append(fn)
        del self.fn_res[0]
        return fn
        
    def IIR_filter_fo(self, value):
        # if len(self.buffer) <= 3:
        #     self.buffer.append(value)
        # else:
        # self.buffer.append(value)
        # del self.buffer[0]
        s1 = 0.05 * value
        fn = (s1 + (self.fn_res[-1] * 0.95))
        self.fn_res.append(fn)
        del self.fn_res[0]
        return fn