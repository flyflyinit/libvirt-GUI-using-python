import libvirt
import sys
import subprocess
from PyQt5.QtWidgets import *
from PyQt5 import QtGui



class GetInformationMain(QMainWindow):

    def __init__(self):
        super().__init__()


    def createConnection(self,host,uri):
        try:
            QMessageBox.information(self, "information","This tool for now supports just QEMU driver for managing KVM guests\nother hypervisors and remote connections will be supported soon!")
            conn = libvirt.open(uri)
            #print(conn.getCapabilities())
            if conn == None:
                QMessageBox.information(self, "information","Failed to open connection to qemu:///system")
                sys.exit(1)
            else:
                return conn
        except Exception as e:
            QMessageBox.critical(self,"error", f"error openning connection with libvirt\n{e}")


    def closeConnection(self,conn):
        conn.close()


    def getDomainDisplayPort(self,dom_name, display_type):
        cmd_str = 'virsh domdisplay %s --type %s' % (dom_name, display_type)
        cmd = subprocess.Popen(f"{cmd_str}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        output = str(cmd.communicate()[0].decode('utf-8'))
        status = str(cmd.returncode)
        if status!='0':
            port = -1
            tls_port = -1
        else:
            _tmp_str = output.split(':')[-1]
            port = int(_tmp_str.split('?')[0])
            if 'tls-port' in _tmp_str:
                tls_port = int(_tmp_str.split('=')[-1])
            else:
                tls_port = -1
        return port, tls_port


    def convert_bytes(self,size):
        for x in ['KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
        return size


    def virDomainList(self,conn,*args):
        global connection
        connection = conn

        self.info_table = list()
        doms = conn.listAllDomains()

        for dom in doms:
            dom_info = list()
            dom_info.append(dom.ID())
            dom_info.append(dom.name())
            dom_info.append(dom.UUIDString())
            info = dom.info()

            state, reason = dom.state()
            if state == libvirt.VIR_DOMAIN_NOSTATE:
                dom_info.append('NO STATE')
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                dom_info.append('RUNNING')
            elif state == libvirt.VIR_DOMAIN_BLOCKED:
                dom_info.append('BLOCKED')
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                dom_info.append('PAUSED')
            elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
                dom_info.append('SHUT DOWN')
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                dom_info.append('SHUT OFF')
            elif state == libvirt.VIR_DOMAIN_CRASHED:
                dom_info.append('CRASHED')
            elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
                dom_info.append('SUSPENDED')
            else:
                dom_info.append('UNKNOWN')

            mem=self.convert_bytes(int(info[2]))
            dom_info.append(mem)

            maxmem = dom.maxMemory()
            if maxmem > 0:
                dom_info.append(self.convert_bytes(maxmem))
            else:
                dom_info.append('ERROR')

            dom_info.append(info[3])
            try:
                maxcpus = dom.maxVcpus()
                if maxcpus != -1:
                    dom_info.append(str(maxcpus))
                else:
                    dom_info.append('ERROR')
            except Exception as e:
                dom_info.append('')

            vnc_port, vnc_tls_port = self.getDomainDisplayPort(dom.name(), 'vnc')
            spice_port, spice_tls_port = self.getDomainDisplayPort(dom.name(), 'spice')
            dom_info.append(vnc_port)
            dom_info.append('%s(%s)' % (spice_port, spice_tls_port))

            self.info_table.append(dom_info)


#####################################################################################################

class PreWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0,0,500,700)
        self.setWindowTitle("Prefrences")
        self.UI()

        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.show()

    def UI(self):
        self.top=QFormLayout()
        self.systemInformation()
        self.layouts()


    def convert_bytes(self,size):
        for x in ['B' ,'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
        return size

    def convert_bytesMB(self,size):
        for x in [ 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
        return size

    def systemInformation(self):
        global connection

        formright = []
        formleft = []

        host = str(connection.getHostname())
        vcpus = str(connection.getMaxVcpus(None))
        nodeinfo = connection.getInfo()
        xmlInfo = str(connection.getSysinfo())
        uri = str(connection.getURI())
        ver = str(connection.getLibVersion())
        freemem = self.convert_bytes(connection.getFreeMemory())
        mem = self.convert_bytesMB(nodeinfo[1])
        map = connection.getCPUMap()

        if connection.isEncrypted() == 1:
            encry = 'True'
        else:
            encry = 'False'

        if connection.isAlive() == 1:
            alive = 'True'
        else:
            alive = 'False'

        if connection.isSecure() == 1:
            secure = 'True'
        else:
            secure = 'False'

        ava = map[1]
        a=''
        for i in range(map[0]):
            if ava[i] == True:
                a = a + f'\ncpu{i}: available'
            else:
                a = a + f'\ncpu{i}: unavailable'


        formleft.append(QLabel('General Informations :'))
        formright.append(QLabel(''))

        formleft.append(QLabel('Hostname :'))
        formright.append(QLabel(host))

        formleft.append(QLabel('Max Support Virtual CPUs :'))
        formright.append(QLabel(vcpus))

        formleft.append(QLabel('Connection URI :'))
        formright.append(QLabel(uri))

        formleft.append(QLabel('Connection Is Encrypted :'))
        formright.append(QLabel(encry))

        formleft.append(QLabel('Connection Is Alive :'))
        formright.append(QLabel(alive))

        formleft.append(QLabel('Connection Is Secure :'))
        formright.append(QLabel(secure))

        formleft.append(QLabel('Virtualization Type :'))
        formright.append(QLabel(str(connection.getType())))

        formleft.append(QLabel('Version :'))
        formright.append(QLabel(str(connection.getVersion())))

        formleft.append(QLabel('Libvirt Version :'))
        formright.append(QLabel(ver))

        formleft.append(QLabel('Model :'))
        formright.append(QLabel(str(nodeinfo[0])))

        formleft.append(QLabel(''))
        formright.append(QLabel(''))

        formleft.append(QLabel('Memory Informations :'))
        formright.append(QLabel(''))

        formleft.append(QLabel('Memory Size :'))
        formright.append(QLabel(mem))

        formleft.append(QLabel('Free Memory :'))
        formright.append(QLabel(freemem))

        formleft.append(QLabel(''))
        formright.append(QLabel(''))

        formleft.append(QLabel('CPU Informations :'))
        formright.append(QLabel(''))

        formleft.append(QLabel('Number Of CPUs :'))
        formright.append(QLabel(str(nodeinfo[2])))

        formleft.append(QLabel('CPU Availability :'))
        formright.append(QLabel(a))

        formleft.append(QLabel('MHz Of CPUs :'))
        formright.append(QLabel(str(nodeinfo[3])))

        formleft.append(QLabel('Number Of NUMA Nodes :'))
        formright.append(QLabel(str(nodeinfo[4])))

        formleft.append(QLabel('CPU Sockets :'))
        formright.append(QLabel(str(nodeinfo[5])))

        formleft.append(QLabel('CPU Cores Per Socket :'))
        formright.append(QLabel(str(nodeinfo[6])))

        formleft.append(QLabel('CPU Threads Per Core :'))
        formright.append(QLabel(str(nodeinfo[7])))



        #VIR_NODE_CPU_STATS_ALL_CPUS to fetch a Python list of statistics for all CPUs
        for cpu in range(map[0]):
            b=''
            stats = connection.getCPUStats(cpu)
            b = b + f"kernel: {str(stats['kernel'])}\n"
            b = b + f"idle: {str(stats['idle'])}\n"
            b = b + f"user: {str(stats['user'])}\n"
            b = b + f"iowait: {str(stats['iowait'])}"
            formleft.append(QLabel(f'CPU {cpu} :'))
            formright.append(QLabel(b))

        c = ''
        stats = connection.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
        c = c + f"kernel: {str(stats['kernel'])}\n"
        c = c + f"idle: {str(stats['idle'])}\n"
        c = c + f"user: {str(stats['user'])}\n"
        c = c + f"iowait: {str(stats['iowait'])}"
        formleft.append(QLabel(f'All CPUs :'))
        formright.append(QLabel(c))
        #self.top3.addRow(QLabel(f'All CPUs :'), QLabel(c))


        for i in range(len(formleft)):
            self.top.addRow(formleft[i], formright[i])



        '''
        nodeinfo = conn.getInfo()
        numnodes = nodeinfo[4]
        memlist = conn.getCellsFreeMemory(0, numnodes)
        cell = 0
        for cellfreemem in memlist:
            print('Node ' + str(cell) + ': ' + str(cellfreemem) + ' bytes free memory')
            cell += 1
        
        domainIDs = connection.listDomainsID()
        if domainIDs == None:
            print('Failed to get a list of domain IDs', file=sys.stderr)
        print("Active domain IDs:")
        if len(domainIDs) == 0:
            print('  None')
        else:
            for domainID in domainIDs:
                print('  ' + str(domainID))

        
        VIR_CONNECT_LIST_DOMAINS_ACTIVE
        VIR_CONNECT_LIST_DOMAINS_INACTIVE
        VIR_CONNECT_LIST_DOMAINS_PERSISTENT
        VIR_CONNECT_LIST_DOMAINS_TRANSIENT
        VIR_CONNECT_LIST_DOMAINS_RUNNING
        VIR_CONNECT_LIST_DOMAINS_PAUSED
        VIR_CONNECT_LIST_DOMAINS_SHUTOFF
        VIR_CONNECT_LIST_DOMAINS_OTHER
        VIR_CONNECT_LIST_DOMAINS_MANAGEDSAVE
        VIR_CONNECT_LIST_DOMAINS_NO_MANAGEDSAVE
        VIR_CONNECT_LIST_DOMAINS_AUTOSTART
        VIR_CONNECT_LIST_DOMAINS_NO_AUTOSTART
        VIR_CONNECT_LIST_DOMAINS_HAS_SNAPSHOT
        VIR_CONNECT_LIST_DOMAINS_NO_SNAPSHOT
        
        print("All (active) domain names:")
        #domains = conn.listAllDomains(0)           # all active and incative domains
        domains = connection.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
        if len(domains) != 0:
            for domain in domains:
                print('The OS type of the domain '+domain.name() +' is ' + domain.OSType() )
        else:
            print('  None')

        
        domName = 'centos7.0'
        dom = conn.lookupByName(domName)
        if dom == None:
            print('Failed to find the domain ' + domName, file=sys.stderr)
            exit(1)
        struct = dom.getTime()
        timestamp = time.ctime(float(struct['seconds']))
        print('The domain current time is ' + timestamp)
        '''



    def layouts(self):
        groupBox = QGroupBox()
        self.top.setContentsMargins(30,30,30,30)     #left ,#top ,#right , #bottom

        groupBox.setLayout(self.top)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        #scroll.setFixedHeight(400)
        self.main=QVBoxLayout()
        self.main.addWidget(scroll)
        self.setLayout(self.main)

