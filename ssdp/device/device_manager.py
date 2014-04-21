import socket
import struct
from threading import Thread
from ssdp.device import Device


class DeviceManager(object):
    def __init__(self):
        self.mcast_address = "239.255.255.250"
        self.mcast_port = 1900
        self.devices = {}
        self.__start_server()

    def add_device(self, device):
        self.devices[device.name] = device

    def __start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, 'SO_REUSEPORT'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind(('', self.mcast_port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcast_address), socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.deviceThread = Thread(target=self.__server_loop).start()

    def __server_loop(self):
        while True:
            read = self.socket.recv(10240)
            header = self.__parse_headers(read)
            if header is not None:
                if 'ST' in header:
                    searching_for_us, found = self.__is_ours(header['ST'])
                    if searching_for_us:
                        print "That's us!"
                        print header['ST']
                        header_string = found.get_notify()
                        self.socket.sendto(header_string, (self.mcast_address, self.mcast_port))
                        print "We sent it!"
                        print header_string

    def __parse_headers(self, buffer):
        # break the data up into lines
        lines = buffer.splitlines()
        # set the type based on the first line
        if lines[0].startswith("M-SEARCH"):
            header = {}
            for line in lines:
                firstColon = line.find(':')
                if firstColon != -1:
                    header[line[:firstColon]] = line[firstColon + 2:]
            return header
        else:
            return None

    def __is_ours(self, st):
        if st == 'ssdp:all':
            return False, None # We are NOT implementing this yet
        if st == 'upnp:rootdevice':
            return False, None  # We are NOT implementing this yet
        if st.startswith('uuid') and len(st) > 5:
            uuid = st[6:]
            uuid_list = self.__get_uuid_list()
            if uuid in uuid_list:
                return True, uuid_list[uuid]
            else:
                return False, None
        if st.startswith('urn') and len(st) > 4:
            urn_list = self.__get_device_service_list()
            if st in urn_list.keys():
                return True, urn_list[st]
        return False, None

    def __get_uuid_list(self):
        uuid_list = {}
        for device in self.devices.itervalues():
            uuid_list[device.uuid] = device
        return uuid_list

    #todo loop through services
    def __get_device_service_list(self):
        urn_list = {}
        for device in self.devices.values():
            urn_list[device.header_nt] = device
        return urn_list



