try:
    import psutil
    import subprocess
except ImportError as e:
    print(f'package not found\n{e}\n')

try:
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.QtWidgets import *
except ImportError as e:
    print(
        f'package PyQt5 Not Found\n{e}\ntry :\npip3 install --user pyqt5\nOR\ndnf install python3-pyqt5, yum install python3-pyqt5\n')

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f'package matplotlib Not Found\n{e}\ntry :\npip3 install --user matplotlib\n')



class PlotsWindow(QWidget):
    def __init__(self,domainname,conn):
        super().__init__()
        self.setGeometry(100, 100, 1100, 600)
        self.setWindowTitle("Plots")

        self.domainname = domainname
        self.dom = conn.lookupByName(self.domainname)

        self.layouts()

    def layouts(self):
        top = QHBoxLayout()

        self.gridSystem = QGridLayout()

        self.memoryC = MemoryCanvas(dom=self.dom,width=6.1, height=3.3, dpi=60)
        #self.diskC = DiskReadWriteCanvas(dom=self.dom,width=6.1, height=3.3, dpi=60)
        #self.cpusC = PolygonCPUs(width=6.1, height=3.3, dpi=60)
        #self.usg = UsageResume(width=6.1, height=3.3, dpi=60)
        #self.read = ReadCanvas(width=6.1, height=3.3, dpi=60)
        #self.write = WriteCanvas(width=6.1, height=3.3, dpi=60)
        self.gridSystem.addWidget(self.memoryC, 0, 0)
        #self.gridSystem.addWidget(self.diskC, 0, 1)
        #self.gridSystem.addWidget(self.cpusC, 0, 2)
        #self.gridSystem.addWidget(self.usg, 1, 0)
        #self.gridSystem.addWidget(self.read, 1, 1)
        #self.gridSystem.addWidget(self.write, 1, 2)

        top.addLayout(self.gridSystem)
        self.setLayout(top)


class MyMplCanvas(FigureCanvas):
    def __init__(self ,parent=None ,dom=None,width=5, height=5, dpi=50):
        fig = Figure(figsize=(width, height), dpi=dpi)
        plt.style.use('Solarize_Light2')
        self.Axes = fig.add_subplot()
        self.compute_initial_figure()


        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MemoryCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self,*args, **kwargs):
        for key, value in kwargs.items():
            if key == 'dom':
                self.dom = value
                self.domainname = self.dom.name()
                self.state = self.dom.state()

        MyMplCanvas.__init__(self, *args, **kwargs)
        self.mem_update_figure()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.mem_update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        #global mem
        #global memtime
        #global memcurrenttime
        #global Axes

        self.mem = []
        self.memtime = []
        self.memcurrenttime = 0
        self.Axes.plot(self.memtime, self.mem)
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Usage 100%")
        #self.Axes.set_title(f"Memory Usage {self.domainname}")
        self.Axes.set_ylim(0, 100)
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        #self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.get_yaxis().set_visible(False)
        self.Axes.legend(loc='upper left')

    def mem_update_figure(self):
        #global mem
        #global memtime
        #global memcurrenttime
        #global Axes

        self.memstats = self.dom.memoryStats()
        print(self.memstats)
        try:
            self.mem.append( int(((self.memstats['usable']) * 100) / self.memstats['actual']))
            print(str( ((self.memstats['usable']) * 100) / self.memstats['actual']))
        except:
            pass


        self.memcurrenttime = self.memcurrenttime + 1
        self.memtime.append(str(self.memcurrenttime))

        if len(self.memtime) == 60:
            self.mem.pop(0)
            self.memtime.pop(0)

        self.Axes.cla()
        self.Axes.plot(self.memtime, self.mem)
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Uasge 100%")
        #self.Axes.set_title(f"Memory Usage {self.domainname}")
        self.Axes.set_ylim(0, 100)
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        #self.Axes.grid(True)
        self.Axes.legend(loc='upper left')
        self.draw()


class CpuCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.cpu_update_figure()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.cpu_update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        global cpuuser
        global cpusystem
        global cpuidle
        global cpuiowait
        global cpuirq
        global cpusoftirq
        global cputimee
        global cpucurrenttime
        global Axes

        cpuuser = []
        cpusystem = []
        cpuiowait = []
        cpuidle = []
        cpuirq = []
        cpusoftirq = []
        cputimee = []
        cpucurrenttime = 0

        self.Axes.plot(cputimee, cpuuser, label='user')
        self.Axes.plot(cputimee, cpusystem, label='system')
        self.Axes.plot(cputimee, cpuidle, label='idle')
        self.Axes.plot(cputimee, cpuiowait, label='iowait')
        self.Axes.plot(cputimee, cpuirq, label='irq')
        self.Axes.plot(cputimee, cpusoftirq, label='softirq')
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Cpu Times")
        self.Axes.set_title("CPU Statistics")
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.legend(loc='upper left')

    def cpu_update_figure(self):
        global cpuuser
        global cpusystem
        global cpuidle
        global cpuiowait
        global cpuirq
        global cpusoftirq
        global cputimee
        global cpucurrenttime
        global Axes

        cpu = psutil.cpu_times()
        cpuuser.append(cpu[0])
        cpusystem.append(cpu[2])
        cpuidle.append(cpu[3])
        cpuiowait.append(cpu[4])
        cpuirq.append(cpu[5])
        cpusoftirq.append(cpu[6])
        cpucurrenttime = cpucurrenttime + 1
        cputimee.append(str(cpucurrenttime))

        if len(cputimee) == 60:
            cpuuser.pop(0)
            cpusystem.pop(0)
            cpuidle.pop(0)
            cpuiowait.pop(0)
            cpuirq.pop(0)
            cpusoftirq.pop(0)
            cputimee.pop(0)

        self.Axes.cla()
        self.Axes.plot(cputimee, cpuuser, label='user')
        self.Axes.plot(cputimee, cpusystem, label='system')
        self.Axes.plot(cputimee, cpuidle, label='idle')
        self.Axes.plot(cputimee, cpuiowait, label='iowait')
        self.Axes.plot(cputimee, cpuirq, label='irq')
        self.Axes.plot(cputimee, cpusoftirq, label='softirq')
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Cpu Times")
        self.Axes.set_title("CPU Statistics")
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.legend(loc='upper left')
        self.draw()


class DiskReadWriteCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self,*args, **kwargs):
        for key, value in kwargs.items():
            if key == 'dom':
                self.dom = value
                self.domainname= self.dom.name()

        MyMplCanvas.__init__(self, *args, **kwargs)

        self.drw_update_figure()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.drw_update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        global read
        global write
        global memtime
        global memcurrenttime
        global Axes

        read = []
        write = []
        memtime = []
        memcurrenttime = 0
        self.Axes.plot(memtime, read, label='read bytes')
        self.Axes.plot(memtime, write, label='write bytes')
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Bytes")
        self.Axes.set_title(f"Disk Read/Write {self.domainname}")
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.legend(loc='upper left')

    def drw_update_figure(self):
        global read
        global write
        global memtime
        global memcurrenttime
        global Axes

        print(self.domainname)
        c = subprocess.run(f"virsh domblklist --domain {self.domainname}"+" | head -n 3 | tail -n 1 | awk {'print $2'}",shell=True,stdout=subprocess.PIPE)
        imagepath = c.stdout.decode('utf-8')
        print(imagepath)
        rd_req, rd_bytes, wr_req, wr_bytes, err = self.dom.blockStats(str(imagepath))
        try:
            read.append(rd_bytes)
        except:
            pass
        try:
            write.append(wr_bytes)
        except:
            pass

        memcurrenttime = memcurrenttime + 1
        memtime.append(str(memcurrenttime))

        if len(memtime) == 60:
            read.pop(0)
            write.pop(0)
            memtime.pop(0)

        self.Axes.cla()
        self.Axes.plot(memtime, read, label='read bytes')
        self.Axes.plot(memtime, write, label='write bytes')
        self.Axes.set_xlabel("Seconds")
        self.Axes.set_ylabel("Bytes")
        self.Axes.set_title(f"Disk Read/Write {self.domainname}")
        self.Axes.set_xlim(0, 60)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        self.Axes.grid(True)
        self.Axes.legend(loc='upper left')
        self.draw()


class UsageResume(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.resume_update_figure()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.resume_update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        global Axes

        people = ('CPU', 'RAM', 'SWAP', 'DISK /')
        y_pos = [0, 1, 2, 3]

        usage = []
        usage.append(psutil.cpu_percent(percpu=False))
        usage.append(psutil.virtual_memory().percent)
        usage.append(psutil.swap_memory().percent)
        usage.append(psutil.disk_usage('/').percent)

        self.Axes.barh(y_pos, usage, align='center')
        self.Axes.set_yticks(y_pos)
        self.Axes.set_yticklabels(people)
        self.Axes.invert_yaxis()
        self.Axes.set_xlabel('Usage 100%')
        self.Axes.set_xlim(0, 100)
        self.Axes.set_title("System Usage")
        self.Axes.grid(True)

    def resume_update_figure(self):
        global Axes
        people = ('CPU', 'RAM', 'SWAP', 'DISK /')
        y_pos = [0, 1, 2, 3]

        usage = []
        usage.append(psutil.cpu_percent(percpu=False))
        usage.append(psutil.virtual_memory().percent)
        usage.append(psutil.swap_memory().percent)
        usage.append(psutil.disk_usage('/').percent)

        self.Axes.cla()
        self.Axes.barh(y_pos, usage, align='center')
        self.Axes.set_yticks(y_pos)
        self.Axes.set_yticklabels(people)
        self.Axes.invert_yaxis()
        self.Axes.set_xlabel('Usage 100%')
        self.Axes.set_xlim(0, 100)
        self.Axes.set_title("System Usage")
        self.Axes.grid(True)
        self.draw()


class PolygonCPUs(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.cpus_update_figure()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.cpus_update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        global logicalcpus
        self.cpuLogicalCount = psutil.cpu_count(logical=True)

        logicalcpus = {}
        for c in range(self.cpuLogicalCount):
            logicalcpus[c] = []

        global cpus
        global cputime
        global cpucurrenttime

        cpus = []

        cputime = []
        cpucurrenttime = 0

        cpu = psutil.cpu_percent(percpu=True)

        i = 0
        for c in logicalcpus:
            logicalcpus[c].append(cpu[i])
            i = i + 1

        cpucurrenttime = cpucurrenttime + 1
        cputime.append(str(cpucurrenttime))
        cpus.append(psutil.cpu_percent())

        i = 0
        for c in logicalcpus:
            self.Axes.plot(cputime, logicalcpus[c], label=f'cpu{str(i)}')
            i = i + 1

        self.Axes.plot(cputime, cpus, label='All CPUs', color='black')
        self.Axes.set_xlim(0, 60)
        self.Axes.set_ylim(0, 100)
        self.Axes.set_xlabel('Seconds')
        self.Axes.set_ylabel('CPUs')
        self.Axes.set_title("CPUs Usage")
        self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        self.Axes.legend(loc='upper left')

    def cpus_update_figure(self):
        global logicalcpus
        global cpus
        global cputime
        global cpucurrenttime

        cpu = psutil.cpu_percent(percpu=True)

        i = 0
        for c in logicalcpus:
            logicalcpus[c].append(cpu[i])
            i = i + 1

        cpucurrenttime = cpucurrenttime + 1
        cputime.append(str(cpucurrenttime))
        cpus.append(psutil.cpu_percent())

        if len(cputime) == 60:
            for c in logicalcpus:
                logicalcpus[c].pop(0)

            cpus.pop(0)
            cputime.pop(0)

        self.Axes.cla()

        i = 0
        for c in logicalcpus:
            self.Axes.plot(cputime, logicalcpus[c], label=f'cpu{str(i)}')
            i = i + 1

        self.Axes.plot(cputime, cpus, label='All CPUs', color='black')
        self.Axes.set_title("CPUs Usage")
        self.Axes.set_xlim(0, 60)
        self.Axes.set_ylim(0, 100)
        self.Axes.set_xlabel('Seconds')
        self.Axes.set_ylabel('CPUs')
        self.Axes.grid(True)
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.legend(loc='upper left')
        self.draw()
