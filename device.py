"""
"""

import settings


try:
    import paramiko
except ImportError:
    print("Could not import paramiko.")


class ManagedDevice:

    def __init__(self, name, ip="127.0.0.1", user="pi", pw=""):

        self.name = name
        self.ip = ip
        self.user = user
        self.pw = pw

        self.connected = False

    def __del__(self):
        self.disconnect()

    def add_property(self, name, value=None):
        setattr(self, name, value)

    def connect(self):

        self.ssh = paramiko.SSHClient()

        if settings.AUTO_ADD_MISSING_HOST:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        try:
            self.ssh.connect(self.ip, username=self.user, password=self.pw)
            self.connected = True
            return True
        except paramiko.ssh_exception.SSHException as e:
            print("Error while trying to connect client:")
            print(str(e))
            return False

    def disconnect(self):
        self.ssh.close()

    def run(self, command):

        if not self.connected:
            raise Exception("SSH Connection has not been established.")

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        except Exception as e:
            print("Could not run command:\n" + str(e))

        return [line for line in stdout] + [line for line in stderr]

    def run_format(self, command):

        try:
            command = command.format(**self.__dict__)
        except Exception as e:
            raise Exception("Could not construct format string:\n" + str(e))

        return self.run(command)


class DeviceGroup:

    def __init__(self, devices):

        self.devices = {device.name: device for device in devices}

        self._iter_devices(lambda device: device.connect())

    def __del__(self):
        self.disconnect()

    def _iter_devices(self, function):

        return {
            name: function(device)
            for name, device in self.devices.items()
        }

    def add_device(self, device):

        self.devices[device.name] = device
        device.connect()

    def remove_device(self, device):

        if type(device) == str:
            del self.devices[device]
        else:
            del self.devices[device.name]

    def run(self, command):

        return self._iter_devices(lambda device: device.run_format(command))

    def disconnect(self):
        self._iter_devices(lambda device: device.disconnect())


def make_group(devices):

    return DeviceGroup([
        ManagedDevice(
            device["name"],
            ip=device["ip"],
            user=device["user"],
            pw=device["pw"])
        for device in devices])
