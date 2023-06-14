import numpy as np

from scipy import signal

import matplotlib.pyplot as plt


# b,a = signal.iirfilter(2, 9, rs=70, analog=False,
#                         btype='lowpass', ftype='cheby2', fs=20)

# print(b, a, sep="\n")






# num = ((self.buffer[-1] * 0.00627527) + (0.00896467 * self.buffer[-2]) + (0.00627527 * self.buffer[-3])) 
# fn = (num + (1.78217688 * self.fn_res[-1]) - (self.fn_res[-2]) * 0.80369209)

# num = ((self.buffer[-1] * 0.00118652) - (0.00154564 * self.buffer[-2]) + (0.00118652 * self.buffer[-3])) 
# fn = (num + (1.95892877 * self.fn_res[-1]) - (self.fn_res[-2]) * 0.95975619)

# num = ((self.buffer[-1] * 0.0003786) - (0.00049318 * self.buffer[-2]) + (0.0003786 * self.buffer[-3])) 
# fn = (num + (1.97689318 * self.fn_res[-1]) - (self.fn_res[-2] * 0.97715719))



val = [1,1,1,1,1,1,1,1,1]
for i in range(0,len(val)):
    if i in range(0,3):
        val[i] = val[i] * 8
    elif i in range(3,6):
        val[i] = val[i] * 2
    elif i in range(6,9):
        val[i] = val[i] * 4
print(val)