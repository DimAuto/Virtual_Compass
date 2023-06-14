import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

class pyPlot(object):
    def __init__(self) -> None:
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(6,1,1)
        self.ax2 = self.fig.add_subplot(6,1,2)
        self.ax3 = self.fig.add_subplot(6,1,3)
        self.ax4 = self.fig.add_subplot(6,1,4)
        self.ax5 = self.fig.add_subplot(6,1,5)
        self.ax6 = self.fig.add_subplot(6,1,6)

    def format_plot(self, min_val=0, max_val=0):
        vals = np.arange(min_val, max_val, 2)
        self.ax1.set(ylabel="X", xlabel="Seconds")#, yticks=vals)
        self.ax2.set(ylabel="Y", xlabel="Seconds")#, yticks=vals)
        self.ax3.set(ylabel="Z", xlabel="Seconds")

    def set_title(self, plt_title):
        self.ax1.set_title(plt_title)

    def plot(self):
        i=0
        while i<100:
            i+=1
            y = np.random.random()
            self.ax.plot(dt.datetime.now().timestamp())
            plt.pause(0.05)
        plt.show()

# p = pyPlot()
# p.set_title("test")
# p.format_plot(x_label="time", y_label="random")
# p.plot()