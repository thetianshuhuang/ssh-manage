"""Device Group class and initializer

Examples
--------
group = DeviceGroup([
    {
        "name": "example1",
        "ip": "1.example",
        "user": "pi",
        "pw": "hunter2",
        "example_attr": "ABC",
    },
    {
        "name": "example2",
        "ip": "2.example",
        "user": "pi",
        "pw": "hunter2",
        "example_attr": "DEF"
    }
])
group.run("echo '{example_attr}'")
"""


from device import ManagedDevice


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

    return DeviceGroup([ManagedDevice(**device) for device in devices])
