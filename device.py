"""Device Manager Classes

Examples
--------
dev = ManageDevice(
    "example_device",
    ip="192.168.0.105",
    user="pi",
    pw="hunter2")
dev.connect()
dev.run("cd /; ls")
"""

import settings


try:
    import paramiko
except ImportError:
    print("Could not import paramiko.")


class ManagedDevice:
    """SSH Managed Device

    Parameters
    ----------
    name : str
        Name of the device; used only by this module (does not need to match
        the device's internal name)
    ip : str
        Target IP.
    user : str
        Username at the target device
    pw : str
        Target device password
    """

    def __init__(self, name, ip="127.0.0.1", user="pi", pw=""):

        self.name = name
        self.ip = ip
        self.user = user
        self.pw = pw

        self.connected = False

    def __del__(self):
        """__del__ method

        Disconnect SSH if this object is garbage collected.
        """

        self.disconnect()

    def add_property(self, name, value=None):
        """Add an arbitrary property to self.

        Parameters
        ----------
        name : str
            Name of property to set
        value : [arbitrary type]
            Value to set
        """

        if name not in ["name", "ip", "user", "pw", "connected", "ssh"]:
            setattr(self, name, value)

    def connect(self):
        """Connect this device.

        Returns
        -------
        bool
            Indicates success or failure
        """

        # Should not connect if already connected.
        if self.connected:
            return False

        self.ssh = paramiko.SSHClient()

        # Check for missing host policy
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
        """Disconnect the device."""

        self.ssh.close()
        self.connected = False

    def run(self, command):
        """Run a command

        Parameters
        ----------
        command : str
            Raw command to execute via ssh

        Returns
        -------
        str[]
            Array of returned values
        """

        if not self.connected:
            raise Exception("SSH Connection has not been established.")

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        except Exception as e:
            print("Could not run command:\n" + str(e))

        return [line for line in stdout] + [line for line in stderr]

    def run_format(self, command):
        """Run a command with format specifiers.

        Format specifiers are fetched from this device's object attributes.
        Built in attributes include ``name``, ``ip``, and ``user``.

        Returns
        -------
        str[]
            Array of returned values
        """

        try:
            command = command.format(**self.__dict__)
        except Exception as e:
            raise Exception("Could not construct format string:\n" + str(e))

        return self.run(command)


class DeviceGroup:
    """Group of devices

    Use this class for programmatic parallel management of a number of
    devices.

    SSH Connections are initiated on init or add; connections are dropped
    on remove or del.

    Parameters
    ----------
    devices : ManagedDevice[]
        Array of devices to manage. Should not be connected.
    """

    def __init__(self, devices):

        self.devices = {device.name: device for device in devices}
        self._iter_devices(lambda device: device.connect())

    def __del__(self):
        """Disconnect function to run on garbage collect

        Prevents garbage collection of the DeviceGroup without first
        terminating the SSH connections.
        """
        self.disconnect()

    def __len__(self):
        """__len__ function for interfacing with Python's ``len`` builtin"""

        return len(self.devices)

    def _iter_devices(self, function):
        """Private function to iterate over all devices.

        Parameters
        ----------
        function : function
            Function to run on all devices
        """

        return {
            name: function(device)
            for name, device in self.devices.items()
        }

    def add_device(self, device):
        """Add a device and start the SSH connection.

        Parameters
        ----------
        device : ManagedDevice
            Device to add
        """

        self.devices[device.name] = device
        device.connect()

    def remove_device(self, device):
        """Remove a device from the SSH connection.

        Parameters
        ----------
        device : ManagedDevice
            Device to remove
        """

        if type(device) == str:
            self.devices[device].disconnect()
            del self.devices[device]
        else:
            device.disconnect()
            del self.devices[device.name]

    def run(self, command):
        """Run a command on all devices.

        Parameters
        ----------
        command : str
            Command to run

        Returns
        -------
        str[][]
            Array of results obtained by ManagedDevice.run_format
        """

        return self._iter_devices(lambda device: device.run_format(command))

    def disconnect(self):
        """Disconnect all devices."""

        self._iter_devices(lambda device: device.disconnect())


def make_group(devices):
    """Make a DeviceGroup from a list of dictionaries.

    Parameters
    ----------
    devices : dict[]
        Each entry should have "name", "ip", "user", and "pw".

    Returns
    -------
    DeviceGroup
        Created DeviceGroup class.
    """

    return DeviceGroup([
        ManagedDevice(
            device["name"],
            ip=device["ip"],
            user=device["user"],
            pw=device["pw"])
        for device in devices])
