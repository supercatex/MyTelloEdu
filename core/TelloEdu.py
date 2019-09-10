#coding=utf-8
import socket
import threading
import time
import netifaces
import netaddr
import pyttsx3


class TelloEdu(object):
    def __init__(self, manager, ip):
        self.manager = manager
        self.ip = ip
        self.sn = ""
        self.name = ""
        self.battery = 0
        self.command = ""
        self.response = ""
        self.next_command = ""

    def send_command(self, command):
        self.command = command
        self.response = ""
        self.manager.send_command(command, self.ip)


class TelloEduManager(object):

    def __init__(self, local_command_port=8889):
        print("Initializing TelloEdu...")
        self.local_command_port = local_command_port
        self.tello_list = []
        self.tts = pyttsx3.init()

        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_socket.bind(("", local_command_port))
        self.command_thread = threading.Thread(target=self._receive_command_thread)
        self.command_thread.setDaemon(True)
        self.command_thread.start()

    def __del__(self):
        self.command_socket.close()

    def _receive_command_thread(self):
        while True:
            try:
                response, address = self.command_socket.recvfrom(2048)
                # print("{}: {}".format(address, response))

                mapping_tello_list = [x for x in self.tello_list if x.ip == address[0]]
                if response == b"ok" and len(mapping_tello_list) == 0:
                    self.tello_list.append(TelloEdu(self, address[0]))
                else:
                    if len(mapping_tello_list) == 0:
                        continue

                    tello = mapping_tello_list[0]
                    tello.response = response.decode("UTF-8")
                    if tello.command == "sn?":
                        tello.sn = response.decode("UTF-8")
                    elif tello.command == "battery?":
                        tello.battery = int(response)

            finally:
                pass

    def send_command(self, command, tello_ip="192.168.10.1", tello_port=8889):
        # print("Send command '{}' to TelloEdu {}:{}.".format(command, tello_ip, tello_port))
        self.command_socket.sendto(command.encode("UTF-8"), (tello_ip, tello_port))

    def find_tello(self):
        print("Finding TelloEdu in your network...")
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if socket.AF_INET not in addresses:
                continue

            info = addresses[socket.AF_INET][0]
            address = info["addr"]
            netmask = info["netmask"]
            if netmask != "255.255.255.0":
                continue

            for ip in netaddr.IPNetwork("%s/%s" % (address, netmask))[99:-1]:
                if str(ip) != address:
                    self.command_socket.sendto("command".encode("UTF-8"), (str(ip), 8889))
        time.sleep(3)
        print("Found {} TelloEdu in your network.".format(len(self.tello_list)))
        time.sleep(1)

    def sn_mapping(self):
        print("Mapping TelloEdu SN...")
        for tello in self.tello_list:
            tello.send_command("sn?")
        self.waiting_for_all_response()
        print("SN mapping finished.")
        time.sleep(1)

    def waiting_for_all_response(self):
        while True:
            mapping_tello_list = [x for x in self.tello_list if x.response == ""]
            if len(mapping_tello_list) == 0:
                break
            time.sleep(0.1)

    def set_tello_name(self, sn, name):
        mapping_tello_list = [x for x in self.tello_list if x.sn == sn]
        for t in mapping_tello_list:
            print("SN:{} named {}.".format(t.sn, name))
            t.name = name

    def get_battery(self):
        print("Getting battery information...")
        for tello in self.tello_list:
            tello.send_command("battery?")
        self.waiting_for_all_response()

    def action(self, name="", delay=0):
        print(name)
        self.tts.say(name)
        self.tts.runAndWait()
        for tello in self.tello_list:
            if tello.next_command == "":
                tello.next_command = "command"
            tello.send_command(tello.next_command)
        self.waiting_for_all_response()
        time.sleep(delay)

    def set_next_command(self, name, command):
        mapping_tello_list = [x for x in self.tello_list if name == "*" or x.name == name]
        for tello in mapping_tello_list:
            tello.next_command = command


if __name__ == "__main__":
    tm = TelloEduManager()
    tm.find_tello()
    if len(tm.tello_list) == 0:
        exit()

    tm.sn_mapping()
    tm.set_tello_name("0TQDG44EDBNYXK", "1")
    tm.get_battery()

    for t in tm.tello_list:
        print(t.ip, t.sn, t.name, t.battery)
