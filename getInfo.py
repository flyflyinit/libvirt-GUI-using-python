import time

import libvirt
import sys
from tabulate import tabulate
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class GetInformationMain(QMainWindow):

    def __init__(self):
        super().__init__()


    def systemInformation(self,conn):
        host = conn.getHostname()
        vcpus = conn.getMaxVcpus(None)
        nodeinfo = conn.getInfo()
        xmlInfo = conn.getSysinfo()
        print(xmlInfo)
        print('Hostname: ' + str(host))
        uri = conn.getURI()
        print('Canonical URI: ' + uri)
        print('Connection is encrypted: ' + str(conn.isEncrypted()))
        print('Connection is secure (A connection will be classified secure if it is either encrypted,\nor it is running on a channel which is not vulnerable to eavesdropping (like a UNIX domain socket): ' + str(conn.isSecure()))
        alive = conn.isAlive()
        print("Connection is alive = " + str(alive))
        print('Virtualization type: ' + conn.getType())
        ver = conn.getVersion()
        print('Version: ' + str(ver))
        ver = conn.getLibVersion();
        print('Libvirt Version: ' + str(ver));
        print('Maximum support virtual CPUs: ' + str(vcpus))
        print('Model: ' + str(nodeinfo[0]))

        print("MEMORY -----------------------------------") ################# MEMORY
        print('Memory size: ' + str(nodeinfo[1]) + ' MB')
        mem = conn.getFreeMemory()
        print("Free memory on the node (host) is " + str(mem) + " bytes.")

        buf = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)
        for parm in buf:
            print(parm)

        print("CPU -----------------------------------") ################# CPU

        print('Number of CPUs: ' + str(nodeinfo[2]))
        print('MHz of CPUs: ' + str(nodeinfo[3]))
        print('Number of NUMA nodes: ' + str(nodeinfo[4]))
        print('Number of CPU sockets: ' + str(nodeinfo[5]))
        print('Number of CPU cores per socket: ' + str(nodeinfo[6]))
        print('Number of CPU threads per core: ' + str(nodeinfo[7]))
        map = conn.getCPUMap()
        print("CPUs: " + str(map[0]))
        print("Available: " + str(map[1]))

        #VIR_NODE_CPU_STATS_ALL_CPUS to fetch a Python list of statistics for all CPUs
        stats = conn.getCPUStats(0)
        print("kernel: " + str(stats['kernel']))
        print("idle:   " + str(stats['idle']))
        print("user:   " + str(stats['user']))
        print("iowait: " + str(stats['iowait']))

        '''
        nodeinfo = conn.getInfo()
        numnodes = nodeinfo[4]
        memlist = conn.getCellsFreeMemory(0, numnodes)
        cell = 0
        for cellfreemem in memlist:
            print('Node ' + str(cell) + ': ' + str(cellfreemem) + ' bytes free memory')
            cell += 1
        '''
        domainIDs = conn.listDomainsID()
        if domainIDs == None:
            print('Failed to get a list of domain IDs', file=sys.stderr)
        print("Active domain IDs:")
        if len(domainIDs) == 0:
            print('  None')
        else:
            for domainID in domainIDs:
                print('  ' + str(domainID))

        '''
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
        '''
        print("All (active) domain names:")
        #domains = conn.listAllDomains(0)           # all active and incative domains
        domains = conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
        if len(domains) != 0:
            for domain in domains:
                print('The OS type of the domain '+domain.name() +' is ' + domain.OSType() )
        else:
            print('  None')

        '''
        domName = 'centos7.0'
        dom = conn.lookupByName(domName)
        if dom == None:
            print('Failed to find the domain ' + domName, file=sys.stderr)
            exit(1)
        struct = dom.getTime()
        timestamp = time.ctime(float(struct['seconds']))
        print('The domain current time is ' + timestamp)
        '''



    def createConnection(self):
        try:
            QMessageBox.information(self, "information","This tool for now supports just QEMU driver for managing KVM guests\nother hypervisors and remote connections will be supported soon!")
            conn = libvirt.open('qemu:///system')
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
