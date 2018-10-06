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


SETTINGS = {
    "AUTO_ADD_MISSING_HOST": True
}


def change_settings(key, value):
    """Change module settings.

    Parameters
    ----------
    key : str
        Key to change
    value : str
        Value to set
    """
    SETTINGS[key] = value


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
    kwargs : dict
        All other keyword args passed directly to object parameters. Names
        cannot be any of the names in PROTECTED_NAMES.
    """

    #: Names that should be protected from add_property.
    PROTECTED_NAMES = [
        "name", "ip", "user", "pw", "connected", "ssh",
        "add_property", "connect", "disconnect", "run", "run_format",
        "__init__", "__del__"]

    def __init__(
            self,
            name="Undefined", ip="127.0.0.1", user="pi", pw="",
            **kwargs):

        self.name = name
        self.ip = ip
        self.user = user
        self.pw = pw

        for key, value in kwargs.items():
            self.add_property(key, value=value)

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

        if name in self.PROTECTED_NAMES:
            raise Exception(
                "Attempted to set protected value of ManagedDevice. "
                "Protected names: " + str(self.PROTECTED_NAMES))
        else:
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
        if SETTINGS["AUTO_ADD_MISSING_HOST"]:
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
