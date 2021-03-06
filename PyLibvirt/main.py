import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
import qtmodern.styles
import qtmodern.windows
import subprocess
from qtpy import QtCore, QtGui
from getInfo import GetInformationMain
from getInfo import PreWindow
import libvirt

from usageplots import PlotsWindow, MemoryCanvas,MyMplCanvas
import psutil

uri='qemu:///system'
host='localhost'


rows=[]
################ disk usage
read = []
write = []
time = []
currenttime = 0
################### cpu usage
cputime = []
cpu1 = []
cpu2 = []
cpu3 = []
cpu4 = []
cpuall = []
cpucurrenttime = 0
################### mem usage
memtime = []
mem = []
memunused = []
memava = []
memrss = []
memswapin = []
memswapout = []
memcurrenttime = 0
################### io usage
iotime = []
ioread = []
iowrite = []
iocurrenttime = 0


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0,0,1500,1000)
        self.setWindowTitle("libvirt GUI")
        self.UI()
        self.show()

    def UI(self):
        global host
        global uri

        self.layouts()
        self.menuBarr()
        self.toolBarr()
        self.toolBarr2()

        self.ins = GetInformationMain()
        self.conn = self.ins.createConnection(host,uri)
        self.memoryC = {}
        self.updateListVM()
        self.startUpdatingTimer()
        #self.ins.systemInformation(self.conn)



    def toolBarr(self):
        tb1 = self.addToolBar("Actions")
        tb1.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        starttb1 = QAction(QIcon("icons/start.png"), "start", self)
        tb1.addAction(starttb1)
        tb1.addSeparator()
        starttb1.triggered.connect(self.startVM)
        suspendtb1 = QAction(QIcon("icons/suspend.png"), "suspend", self)
        tb1.addAction(suspendtb1)
        tb1.addSeparator()
        suspendtb1.triggered.connect(self.suspendVM)
        resumetb1 = QAction(QIcon("icons/resume.png"), "resume", self)
        tb1.addAction(resumetb1)
        tb1.addSeparator()
        tb1.addSeparator()
        tb1.addSeparator()
        resumetb1.triggered.connect(self.resumeVM)
        shutdowntb1 = QAction(QIcon("icons/shutdown.png"), "shutdown", self)
        tb1.addAction(shutdowntb1)
        tb1.addSeparator()
        shutdowntb1.triggered.connect(self.shutdownVM)
        destroytb1 = QAction(QIcon("icons/destroy.png"), "destroy", self)
        tb1.addAction(destroytb1)
        tb1.addSeparator()
        destroytb1.triggered.connect(self.destroyVM)
        reboottb1 = QAction(QIcon("icons/reboot.png"), "reboot", self)
        tb1.addAction(reboottb1)
        tb1.addSeparator()
        tb1.addSeparator()
        tb1.addSeparator()
        reboottb1.triggered.connect(self.rebootVM)

        savetb1 = QAction(QIcon("icons/save.png"), "save", self)
        tb1.addAction(savetb1)
        savetb1.triggered.connect(self.saveVM)
        tb1.addSeparator()
        restoretb1 = QAction(QIcon("icons/restore.png"), "restore", self)
        tb1.addAction(restoretb1)
        restoretb1.triggered.connect(self.restoreVM)
        tb1.addSeparator()
        resettb1 = QAction(QIcon("icons/reset.png"), "reset", self)
        tb1.addAction(resettb1)
        resettb1.triggered.connect(self.resetVM)
        tb1.addSeparator()


    def toolBarr2(self):
        tb2 = self.addToolBar("Statistics")
        self.addToolBar(QtCore.Qt.BottomToolBarArea, tb2)

        tb2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        disktb2 = QAction(QIcon("icons/disk.png"), "Disk Usage", self)
        tb2.addAction(disktb2)
        disktb2.triggered.connect(self.DiskU)

        iotb2 = QAction(QIcon("icons/io.png"), "I/O Usage", self)
        tb2.addAction(iotb2)
        iotb2.triggered.connect(self.IOUsage)

        memorytb2 = QAction(QIcon("icons/ram.png"), "Memory Usage", self)
        tb2.addAction(memorytb2)
        memorytb2.triggered.connect(self.MemoryUsage)

        cputb2 = QAction(QIcon("icons/cpu.png"), "Cpu Usage", self)
        tb2.addAction(cputb2)
        cputb2.triggered.connect(self.VCPUsage)


    def menuBarr(self):
        menuB = self.menuBar()
        file = menuB.addMenu("File")
        edit = menuB.addMenu("Edit")
        help = menuB.addMenu("Help")

        pre = QAction("Prefrences", self)
        pre.setShortcut("Ctrl+P")
        pre.triggered.connect(self.prefrences)
        file.addAction(pre)

        rename = QAction("rename", self)
        file.addAction(rename)
        delete = QAction("delete", self)
        file.addAction(delete)

        exitt = QAction("Exit", self)
        file.addAction(exitt)
        exitt.setIcon(QIcon("icons/cancel.svg"))
        exitt.triggered.connect(self.exit)



    def prefrences(self):
        pw = PreWindow()
        pww = qtmodern.windows.ModernWindow(pw)
        pww.show()




################################################################## VM actions ##################################
    def startVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh start --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} started succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during starting {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during starting {domain} domain\n{e}")

    def suspendVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh suspend --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} suspended succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during suspending {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during suspending {domain} domain\n{e}")

    def shutdownVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh shutdown --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} stoped succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during stoping {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during stoping {domain} domain\n{e}")

    def destroyVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh destroy --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} destored succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during destroying {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during destroying {domain} domain\n{e}")


    def saveVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain = row[1]
            dom = self.conn.lookupByName(domain)
            state, reason = dom.state()
            if state == libvirt.VIR_DOMAIN_SHUTOFF:
                QMessageBox.warning(self,'warning','Not saving guest that is not running')
            else:
                url = QFileDialog.getSaveFileName(self, "save a savepoint", "/var/lib/libvirt/qemu/save/", "Image Files(*img)")
                if url[0] != '':
                    path = url[0] + ".img"
                    try:
                        s = subprocess.run(f"virsh save --domain {domain} --file {path}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                        #w2=Window2()
                        #mw = qtmodern.windows.ModernWindow(w2)
                        #mw.show()
                        if str(s.returncode)=='0':
                            QMessageBox.information(self,"success",f"{domain} saved succefully!\nIn the following path {path}")
                        else:
                            QMessageBox.critical(self, "ERROR", f"error occured during saving {domain} domain\n{s.stdout}\n{s.stderr}")
                    except Exception as e :
                        QMessageBox.critical(self,"ERROR",f"error occured during saving {domain} domain\n{e}")


    def restoreVM(self):
        url = QFileDialog.getOpenFileName(self, "select a savepoint file to restore", "/var/lib/libvirt/qemu/save/", "Image Files(*img)")
        if url[0] != '':
            path=url[0]
            try:
                s = subprocess.run(f"virsh restore --file {path}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{path} restored succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during restoring {path} \n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during restoring {path} \n{e}")



    def resumeVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh resume --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} resumed succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during resuming {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during resuming {domain} domain\n{e}")


    def resetVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain=row[1]
            try:
                s = subprocess.run(f"virsh reset --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} reseted succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during reseting {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during reseting {domain} domain\n{e}")


    def rebootVM(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain = row[1]
            try:
                s = subprocess.run(f"virsh reboot --domain {domain}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if str(s.returncode)=='0':
                    QMessageBox.information(self,"success",f"{domain} rebooted succefully!")
                else:
                    QMessageBox.critical(self, "ERROR", f"error occured during rebooting {domain} domain\n{s.stdout}\n{s.stderr}")
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during rebooting {domain} domain\n{e}")


    def enableAutoStart(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain = row[1]
            try:
                self.dom = self.conn.lookupByName(domain)
                if self.dom.autostart() == 1:
                    QMessageBox.warning(self,'warning',f'autostart already enabled in {domain} domain')
                else:
                    self.dom.setAutostart(1)
                    QMessageBox.information(self, 'success', f'autostart enabled succesfully in domain {domain}')
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during enabling autostart to {domain} domain\n{e}")


    def disableAutoStart(self):
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            row = rows[a]
            domain = row[1]
            try:
                self.dom = self.conn.lookupByName(domain)
                if self.dom.autostart() == 0:
                    QMessageBox.warning(self,'warning',f'autostart already disabled in {domain} domain')
                else:
                    self.dom.setAutostart(0)
                    QMessageBox.information(self, 'success', f'autostart disabled succesfully in domain {domain}')
            except Exception as e :
                QMessageBox.critical(self,"ERROR",f"error occured during disabling autostart to {domain} domain\n{e}")


    ###########################################################################################################################


    def layouts(self):

        self.mainLayout=QVBoxLayout()
        self.topLayout=QHBoxLayout()
        self.bottomLayout=QHBoxLayout()

        self.table=QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(12)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setAutoFillBackground(True)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)

        self.table.setHorizontalHeaderItem(0,QTableWidgetItem("ID"))
        self.table.setHorizontalHeaderItem(1,QTableWidgetItem("NAME"))
        self.table.setHorizontalHeaderItem(2,QTableWidgetItem("UUID"))
        self.table.setHorizontalHeaderItem(3,QTableWidgetItem("STATUS"))
        self.table.setHorizontalHeaderItem(4,QTableWidgetItem("MEMORY"))
        self.table.setHorizontalHeaderItem(5,QTableWidgetItem("MAX MEMORY"))
        self.table.setHorizontalHeaderItem(6,QTableWidgetItem("VCPUs"))
        self.table.setHorizontalHeaderItem(7,QTableWidgetItem("MAX VCPUs"))
        self.table.setHorizontalHeaderItem(8,QTableWidgetItem("VNC"))
        self.table.setHorizontalHeaderItem(9,QTableWidgetItem("SPICE"))
        self.table.setHorizontalHeaderItem(10,QTableWidgetItem("GUI"))
        self.table.setHorizontalHeaderItem(11,QTableWidgetItem("USAGE"))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.table.resizeColumnsToContents()
        #self.table.resizeRowsToContents()
        self.table.setCurrentCell(-1,-1)

        self.topLayout.addWidget(self.table)
        #self.topLayout.addLayout(self.gridSystem)
        self.setCentralWidget(self.table)

        #self.bottomLayout.addWidget(self.title)
        #self.setCentralWidget(self.title)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.bottomLayout)
        self.setLayout(self.mainLayout)



    def contextMenuEvent(self,event):
        self.table.menuu = QMenu(self.table)
        opengui = QAction('Open GUI', self.table)
        enableAS = QAction('Enable autostart', self.table)
        disableAS = QAction('Disable autostart', self.table)
        start = QAction('Start', self.table)
        suspend = QAction('Suspend', self.table)
        resume = QAction('Resume', self.table)
        shutdown = QAction('Shutdown', self.table)
        destroy = QAction('Destroy', self.table)
        reboot = QAction('Reboot', self.table)
        save = QAction('Save', self.table)
        reset = QAction('Reset', self.table)
        opengui.triggered.connect(self.connectGUI)
        self.table.menuu.addAction(opengui)
        enableAS.triggered.connect(self.enableAutoStart)
        self.table.menuu.addAction(enableAS)
        disableAS.triggered.connect(self.disableAutoStart)
        self.table.menuu.addAction(disableAS)
        start.triggered.connect(self.startVM)
        self.table.menuu.addAction(start)
        suspend.triggered.connect(self.suspendVM)
        self.table.menuu.addAction(suspend)
        resume.triggered.connect(self.resumeVM)
        self.table.menuu.addAction(resume)
        shutdown.triggered.connect(self.shutdownVM)
        self.table.menuu.addAction(shutdown)
        destroy.triggered.connect(self.destroyVM)
        self.table.menuu.addAction(destroy)
        reboot.triggered.connect(self.rebootVM)
        self.table.menuu.addAction(reboot)
        save.triggered.connect(self.saveVM)
        self.table.menuu.addAction(save)
        reset.triggered.connect(self.resetVM)
        self.table.menuu.addAction(reset)

        self.table.menuu.popup(QtGui.QCursor.pos())


    def startUpdatingTimer(self):
        self.timerr = QTimer(self)
        self.timerr.start()
        self.timerr.setInterval(10000)
        self.timerr.timeout.connect(self.updateListVM)

    def updateListVM(self):
        self.table.setCurrentCell(-1,-1)
        global rows
        rowPosition = 0
        self.table.setRowCount(0)
        self.ins.virDomainList(self.conn)
        rows = self.ins.info_table
        for self.row in rows:
            self.dom = self.conn.lookupByName(self.row[1])
            self.domainname = self.dom.name()
            self.rowPosition = self.table.rowCount()
            self.table.insertRow(self.rowPosition)
            self.table.setItem(self.rowPosition, 0, QTableWidgetItem(str(self.row[0])))
            self.table.setItem(self.rowPosition, 1, QTableWidgetItem(str(self.row[1])))
            self.table.setItem(self.rowPosition, 2, QTableWidgetItem(str(self.row[2])))
            self.table.setItem(self.rowPosition, 3, QTableWidgetItem(str(self.row[3])))
            self.table.setItem(self.rowPosition, 4, QTableWidgetItem(str(self.row[4])))
            self.table.setItem(self.rowPosition, 5, QTableWidgetItem(str(self.row[5])))
            self.table.setItem(self.rowPosition, 6, QTableWidgetItem(str(self.row[6])))
            self.table.setItem(self.rowPosition, 7, QTableWidgetItem(str(self.row[7])))
            self.table.setItem(self.rowPosition, 8, QTableWidgetItem(str(self.row[8])))
            self.table.setItem(self.rowPosition, 9, QTableWidgetItem(str(self.row[9])))

            self.table.setRowHeight(self.rowPosition,80)

            self.btn=QPushButton("Open")
            self.btn.clicked.connect(self.connectGUI)
            self.table.setCellWidget(self.rowPosition, 10,self.btn)
            #self.usage=QPushButton("Show")
            #self.usage.clicked.connect(self.ShowUsage)
            #self.table.setCellWidget(self.rowPosition, 11,self.usage)
            state = self.row[3]
            #if state != 'SHUT DOWN' and state != 'SHUT OFF' and state!='PAUSED':
            if state == 'RUNNING':
                print(self.domainname)
                print(self.memoryC.keys())
                if self.domainname in self.memoryC.keys():
                    self.memoryC[self.domainname].dom = self.dom
                    self.table.setCellWidget(self.rowPosition, 11, self.memoryC[self.domainname])
                    print("already exist"+str(self.domainname)+"   "+str(self.dom.name()))
                else:
                    self.memoryC[self.domainname] = MemoryCanvas(dom=self.dom, width=3, height=3.3, dpi=20)
                    self.table.setCellWidget(self.rowPosition, 11, self.memoryC[self.domainname])
            else:
                pass

    def ShowUsage(self):
        global host
        global uri

        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                state = row[3]
                if state != 'SHUT DOWN' and state != 'SHUT OFF':
                    self.plotswindow = PlotsWindow(domain,self.conn)
                    self.pw = qtmodern.windows.ModernWindow(self.plotswindow)
                    self.pw.show()
                    '''
                    vnc = str(row[8])
                    spice = str(row[9])
                    spiceport = str(spice.split('(')[0])
                    vncport = str(vnc.split('(')[0])
                    if spiceport!='-1':
                        subprocess.run(f'spicy --uri={uri} -h {host} -p {spiceport}',shell=True)
                    elif vncport!='-1':
                        c = subprocess.run(f'virsh vncdisplay {domain}',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                        out=str(c.stdout.decode('utf-8'))
                        # tiger vnc client
                        subprocess.run(f'vncviewer {out}',shell=True)
                    else:
                        QMessageBox.warning(self, 'warning', f'domain {domain}, Failed to get VNC port, and SPICE port. Is this domain using VNC or SPICE ?')
                    '''
                else:
                    QMessageBox.warning(self,'warning',f'domain {domain} is not running')
            except Exception as e:
                QMessageBox.critical(self, 'error', f'error occured \n{e}')

    def connectGUI(self):
        global host
        global uri

        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                state = row[3]
                if state != 'SHUT DOWN' and state != 'SHUT OFF':
                    vnc = str(row[8])
                    spice = str(row[9])
                    spiceport = str(spice.split('(')[0])
                    vncport = str(vnc.split('(')[0])
                    if spiceport!='-1':
                        subprocess.run(f'spicy --uri={uri} -h {host} -p {spiceport}',shell=True)
                    elif vncport!='-1':
                        c = subprocess.run(f'virsh vncdisplay {domain}',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                        out=str(c.stdout.decode('utf-8'))
                        # tiger vnc client
                        subprocess.run(f'vncviewer {out}',shell=True)
                    else:
                        QMessageBox.warning(self, 'warning', f'domain {domain}, Failed to get VNC port, and SPICE port. Is this domain using VNC or SPICE ?')
                else:
                    QMessageBox.warning(self,'warning',f'domain {domain} is not running')
            except Exception as e:
                QMessageBox.critical(self, 'error', f'error occured \n{e}')

    ############################################################################## Disk Usage ###########################
    def animateDisk(self,i):
        from matplotlib.ticker import ScalarFormatter
        global read
        global write
        global time
        global currenttime
        global plt
        global ax1
        global ani

        rd_req, rd_bytes, wr_req, wr_bytes, err = self.dom.blockStats(self.imagepath)
        read.append(rd_bytes)
        write.append(wr_bytes)
        currenttime=currenttime+1
        time.append(str(currenttime))

        if len(time) == 60:
            time.pop(0)
            read.pop(0)
            write.pop(0)

        ax1.clear()
        ax1.plot(time, read, label='Disk Read', color='green')
        ax1.plot(time, write, label='Disk Write', color='blue')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        plt.xlabel("Seconds")
        plt.ylabel('Bytes')
        plt.title(f"Disk Usage {self.domname}")
        plt.grid(True)
        plt.legend()

    def DiskU(self):
        global read
        global write
        global time
        global currenttime
        global plt
        global ax1
        global ani
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                self.dom = self.conn.lookupByName(domain)
                state, reason = self.dom.state()
                self.domname = self.dom.name()
                self.imagepath = f'/var/lib/libvirt/images/{self.domname}.qcow2'
                if state != libvirt.VIR_DOMAIN_SHUTOFF and state != libvirt.VIR_DOMAIN_SHUTDOWN:
                    import matplotlib.pyplot as plt
                    import matplotlib.animation as animation
                    from matplotlib.ticker import ScalarFormatter
                    read = []
                    write = []
                    time = []
                    currenttime = 0
                    fig = plt.figure(f"Disk Usage {self.domname}")
                    ax1 = fig.add_subplot(1, 1, 1)
                    ani = animation.FuncAnimation(fig, self.animateDisk, interval=1000)
                    plt.xlabel("Seconds")
                    plt.ylabel('Bytes',labelpad=500)
                    plt.title(f"Disk Usage {self.domname}")
                    plt.grid(True)
                    plt.legend()
                    plt.show()
                else:
                    QMessageBox.warning(self,'warning',f'domain {self.domname} is not running')
            except Exception as e :
                QMessageBox.critical(self,'error',f'error occured \n{e}')

############################################################################ CPU usage ################################
    def animateCPU(self,i):
        from matplotlib.ticker import ScalarFormatter
        global cpuall
        global cpu1
        global cpu2
        global cpu3
        global cpu4
        global cputime
        global cpucurrenttime
        global cpuplt
        global cpuax1
        global cpuani

        map = self.conn.getCPUMap()

        print("CPUs: " + str(map[0]))
        print("Available: " + str(map[1]))

        #cpu_stats = self.dom.getCPUStats(False)
        #print(cpu_stats)
        '''
        for (i, cpu) in enumerate(cpu_stats):
            print('CPU ' + str(i) + ' Time: ' + str(cpu['cpu_time'] / 1000000000.))
        '''

        stats = self.dom.getCPUStats(0)
        print("kernel: " + str(stats['kernel']))
        print("idle:   " + str(stats['idle']))
        print("user:   " + str(stats['user']))
        print("iowait: " + str(stats['iowait']))

        cpus=[]
        cpu_stats = self.dom.getCPUStats(True)
        for (i, cpu) in enumerate(cpu_stats):
            #print('CPU ' + str(i) + ' Time: ' + str(cpu['cpu_time'] / 1000000000.))
            cpus.append(cpu['cpu_time'])
        sum=(cpus[0]+cpus[1]+cpus[2]+cpus[3])/4
        cpu1.append(cpus[0])
        cpu2.append(cpus[1])
        cpu3.append(cpus[2])
        cpu4.append(cpus[3])

        cpuall.append(sum)
        cpucurrenttime=cpucurrenttime+1
        cputime.append(str(cpucurrenttime))

        if len(cputime) == 60:
            cputime.pop(0)
            cpu1.pop(0)
            cpu2.pop(0)
            cpu3.pop(0)
            cpu4.pop(0)
            cpuall.pop(0)

        cpuax1.clear()
        cpuax1.plot(cputime, cpu1, label='CPU 0', color='green')
        cpuax1.plot(cputime, cpu2, label='CPU 1', color='blue')
        cpuax1.plot(cputime, cpu3, label='CPU 2', color='red')
        cpuax1.plot(cputime, cpu4, label='CPU 3', color='gray')
        cpuax1.plot(cputime, cpuall, label='All CPUs', color='black')
        cpuplt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        cpuplt.xlabel("Seconds")
        cpuplt.ylabel('CPU Time')
        cpuplt.title(f"CPU Usage {self.domname}")
        cpuplt.grid(True)
        cpuplt.legend()

    def VCPUsage(self):
        global cpu1
        global cpu2
        global cpu3
        global cpu4
        global cpuall
        global cputime
        global cpucurrenttime
        global cpuplt
        global cpuax1
        global cpuani
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                self.dom = self.conn.lookupByName(domain)
                state, reason = self.dom.state()
                self.domname = self.dom.name()

                if state != libvirt.VIR_DOMAIN_SHUTOFF and state != libvirt.VIR_DOMAIN_SHUTDOWN:
                    import matplotlib.pyplot as cpuplt
                    import matplotlib.animation as animation
                    from matplotlib.ticker import ScalarFormatter
                    cpu1 = []
                    cpu2 = []
                    cpu3 = []
                    cpu4 = []
                    cpuall = []
                    cputime = []
                    cpucurrenttime = 0
                    cpufig = cpuplt.figure(f"CPU Usage {self.domname}")
                    cpuax1 = cpufig.add_subplot(1, 1, 1)
                    cpuani = animation.FuncAnimation(cpufig, self.animateCPU, interval=1000)
                    cpuplt.xlabel("Seconds")
                    cpuplt.ylabel('Bytes')
                    cpuplt.title(f"CPU Usage {self.domname}")
                    cpuplt.grid(True)
                    cpuplt.legend()
                    cpuplt.show()
                else:
                    QMessageBox.warning(self,'warning',f'domain {self.domname} is not running')
            except Exception as e :
                QMessageBox.critical(self,'error',f'error occured \n{e}')

##################################################################### Memory Usage #######################
    def animateMemory(self,i):
        from matplotlib.ticker import ScalarFormatter
        global mem
        global memswapin
        global memswapout
        global memunused
        global memava
        global memrss
        global memtime
        global memcurrenttime
        global memplt
        global memax1
        global memani

        memstats = self.dom.memoryStats()
        print(memstats)
        if (len(memstats)==4):
            mem.append(memstats['actual'])
            memswapin.append(memstats['swap_in'])
            memrss.append(memstats['rss'])
            memcurrenttime = memcurrenttime + 1
            memtime.append(str(memcurrenttime))

            if len(memtime) == 60:
                memtime.pop(0)
                mem.pop(0)
                memswapin.pop(0)
                memrss.pop(0)

            memax1.clear()
            memax1.plot(memtime, mem, label='actual', color='black')
            memax1.plot(memtime, memswapin, label='swap in', color='red')
            memax1.plot(memtime, memrss, label='rss', color='brown')

        else:
            mem.append(memstats['actual'])
            memswapin.append(memstats['swap_in'])
            memswapout.append(memstats['swap_out'])
            memunused.append(memstats['unused'])
            memava.append(memstats['available'])
            memrss.append(memstats['rss'])
            memcurrenttime=memcurrenttime+1
            memtime.append(str(memcurrenttime))

            if len(memtime) == 60:
                memtime.pop(0)
                mem.pop(0)
                memswapin.pop(0)
                memswapout.pop(0)
                memunused.pop(0)
                memava.pop(0)
                memrss.pop(0)

            memax1.clear()
            memax1.plot(memtime, mem, label='actual', color='black')
            memax1.plot(memtime, memswapin, label='swap in', color='red')
            memax1.plot(memtime, memswapout, label='swap out', color='green')
            memax1.plot(memtime, memunused, label='unused', color='gray')
            memax1.plot(memtime, memava, label='available', color='blue')
            memax1.plot(memtime, memrss, label='rss', color='brown')

        memplt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        memplt.xlabel("Seconds")
        memplt.ylabel('Memory')
        memplt.title(f"Memory Usage {self.domname}")
        memplt.grid(True)
        memplt.legend()

    def MemoryUsage(self):
        global mem
        global memswapin
        global memswapout
        global memunused
        global memava
        global memrss
        global memtime
        global memcurrenttime
        global memplt
        global memax1
        global memani
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                self.dom = self.conn.lookupByName(domain)
                state, reason = self.dom.state()
                self.domname = self.dom.name()

                if state != libvirt.VIR_DOMAIN_SHUTOFF and state != libvirt.VIR_DOMAIN_SHUTDOWN:
                    import matplotlib.pyplot as memplt
                    import matplotlib.animation as animation
                    from matplotlib.ticker import ScalarFormatter
                    mem = []
                    memswapin = []
                    memswapout = []
                    memunused = []
                    memava = []
                    memrss = []
                    memtime = []
                    memcurrenttime = 0
                    memfig = memplt.figure(f"Memory Usage {self.domname}")
                    memax1 = memfig.add_subplot(1, 1, 1)
                    memani = animation.FuncAnimation(memfig, self.animateMemory, interval=1000)
                    memplt.xlabel("Seconds")
                    memplt.ylabel('Memory')
                    memplt.title(f"Memory Usage {self.domname}")
                    memplt.grid(True)
                    memplt.legend()
                    memplt.show()
                else:
                    QMessageBox.warning(self,'warning',f'domain {self.domname} is not running')
            except Exception as e :
                QMessageBox.critical(self,'error',f'error occured \n{e}')

################################################################### IO Usage ##########################
    def animateIO(self,i):
        from xml.etree import ElementTree
        global ioread
        global iowrite
        global iotime
        global iocurrenttime
        global ioplt
        global ioax1
        global ioani

        from xml.etree import ElementTree
        tree = ElementTree.fromstring(self.dom.XMLDesc())
        iface = tree.find('devices/interface/target').get('dev')
        stats = self.dom.interfaceStats(iface)

        ioread.append(stats[0])
        iowrite.append(stats[4])

        iocurrenttime=iocurrenttime+1
        iotime.append(str(iocurrenttime))

        if len(iotime) == 60:
            iotime.pop(0)
            ioread.pop(0)
            iowrite.pop(0)

        ioax1.clear()
        ioax1.plot(iotime, ioread, label='I/O read', color='blue')
        ioax1.plot(iotime, iowrite, label='I/O write', color='red')
        ioplt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
        ioplt.xlabel("Seconds")
        ioplt.ylabel('Bytes')
        ioplt.title(f"I/O Usage {self.domname}")
        ioplt.grid(True)
        ioplt.legend()

    def IOUsage(self):
        global ioread
        global iowrite
        global iotime
        global iocurrenttime
        global ioplt
        global ioax1
        global ioani
        a = self.table.currentRow()
        self.table.setCurrentCell(-1,-1)
        if a==-1:
            QMessageBox.warning(self,"warning","please select a VM")
        else:
            try:
                row = rows[a]
                domain = row[1]
                self.dom = self.conn.lookupByName(domain)
                state, reason = self.dom.state()
                self.domname = self.dom.name()

                if state != libvirt.VIR_DOMAIN_SHUTOFF and state != libvirt.VIR_DOMAIN_SHUTDOWN:
                    import matplotlib.pyplot as ioplt
                    import matplotlib.animation as animation
                    from matplotlib.ticker import ScalarFormatter
                    ioread = []
                    iowrite = []
                    iotime = []
                    iocurrenttime = 0
                    iofig = ioplt.figure(f"I/O Usage {self.domname}")
                    ioax1 = iofig.add_subplot(1, 1, 1)
                    ioani = animation.FuncAnimation(iofig, self.animateIO, interval=1000)
                    ioplt.xlabel("Seconds")
                    ioplt.ylabel('Bytes')
                    ioplt.title(f"I/O Usage {self.domname}")
                    ioplt.grid(True)
                    ioplt.legend()
                    ioplt.show()
                else:
                    QMessageBox.warning(self,'warning',f'domain {self.domname} is not running')
            except Exception as e :
                QMessageBox.critical(self,'error',f'error occured \n{e}')

    def exit(self):
        qst=QMessageBox.question(self,"Warning","Are You Sure To Exit", QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if qst==QMessageBox.Yes:
            self.ins.closeConnection(self.conn)
            self.close()


def main():
    App = QApplication(sys.argv)
    w = Window()
    qtmodern.styles.dark(App)
    #qtmodern.styles.light(App)
    mw = qtmodern.windows.ModernWindow(w)
    mw.show()
    sys.exit(App.exec_())

if __name__ == '__main__':
    main()