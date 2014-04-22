import socket
import uuid
import sys
import notify

class Device(notify.noitfy):
    def __init__(self,
                 name,
                 iface=None,
                 uuid=None,
                 domain_name="schemas-upnp-org",
                 device_type="Basic",
                 version="1.0"):
        self.name = name
        self.domain_name = domain_name

        if iface is None:
            iface = self.__getLocalIPAddress()
        self.iface = iface

        if uuid is None:
            uuid = self.__generate_uuid()
        self.uuid = uuid

        self.device_type = device_type
        self.device_version = version
        self.header_nt = "urn:" + domain_name + ":device:" + \
                         self.device_type + ":" + self.device_version
        self.services = {}

    def get_notify(self):
        headers = self.__generate_headers()
        header_string = "NOTIFY * HTTP/1.1\r\n"
        for key, value in headers.iteritems():
            header_string += key + ": " + value + "\r\n"
        header_string += "\r\n"
        return header_string


    def __generate_headers(self):
        headers = {}
        headers['HOST'] = "239.255.255.250:1900"
        headers['CACHE-CONTROL'] = "max-age=1800"
        headers['LOCATION'] = self.__get_info_url()
        headers['NT'] = self.header_nt #"uuid:" + str(self.uuid)
        headers['NTS'] = "ssdp:alive"
        headers['SERVER'] = "python/" + str(sys.version_info.major) + "." + str(sys.version_info.minor) + " UPnP/1.0 product/version"  # We should give an actual product and version
        headers['USN'] = "uuid:" + str(self.uuid)

        return headers

    def __get_info_url(self):
        return "http://" + self.iface + ":1990/description/fetch"

    def __getLocalIPAddress(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except socket.error as ex:
            ip = None
        return ip

    def __generate_uuid(self):
        return uuid.uuid1()