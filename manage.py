"""Device Manager Script

Command line tool for device management. Device definitions should be
stored in ``settings.py``.

Examples
--------
[SSHM] 2 devices connected.

SSH Group | echo '{name}'
device_1 > device_1

device_2 > device_2

SSH Group | cd ~; ls
device_1 > [no output]

device_2 > test_folder
           secrets.txt
           test_file.py

SSH Group | cd ~/test_folder; ls
device_1 > bash: cd: test_folder: No such file or directory

device_2 > a.out
           program.c

SSH Group | exit

[SSHM] 2 devices disconnected.
"""


import sys
import importlib
import readline

from group import make_group


AUTHOR = "Tianshu Huang"
DATE = "Fall 2018"


def _splash():
    """Display splash text"""

    print(r"""
      ___           ___           ___           ___
     /  /\         /  /\         /__/\         /__/\
    /  /:/_       /  /:/_        \  \:\       |  |::\
   /  /:/ /\     /  /:/ /\        \__\:\      |  |:|:\
  /  /:/ /::\   /  /:/ /::\   ___ /  /::\   __|__|:|\:\
 /__/:/ /:/\:\ /__/:/ /:/\:\ /__/\  /:/\:\ /__/::::| \:\
 \  \:\/:/~/:/ \  \:\/:/~/:/ \  \:\/:/__\/ \  \:\~~\__\/
  \  \::/ /:/   \  \::/ /:/   \  \::/       \  \:\
   \__\/ /:/     \__\/ /:/     \  \:\        \  \:\
     /__/:/        /__/:/       \  \:\        \  \:\
     \__\/         \__\/         \__\/         \__\/
     {author}, {date}
""".format(author=AUTHOR, date=DATE))


class ManageCLI:
    """Command line class

    Parameters
    ----------
    cfg : module
        Module to load groups from
    """

    def __init__(self, cfg):

        _splash()
        self.connect(cfg)

    def connect(self, cfg):
        """Connect all groups

        Parameters
        ----------
        cfg : module
            Module to load groups from
        """

        print("  [SSHM] Connecting...")

        # Create groups
        self.groups = {
            key: make_group(value)
            for key, value in cfg.__dict__.items() if key[0] != "_"
        }

        # Set current group
        try:
            self.current = getattr(cfg, "_DEFAULT")
        except AttributeError:
            self.current = self.groups.keys()[0]

        # Print connect status
        for name, group in self.groups.items():
            print(
                "  [{name}] {n} devices connected.\n"
                .format(name=name, n=len(group)))

    def disconnect(self):
        """Disconnect all groups"""

        for name, group in self.groups.items():
            group.disconnect()
            print(
                "  [{name}] {n} devices disconnected."
                .format(name=name, n=len(group)))
        print("  [SSHM] All groups disconnected.")

    def exec_command(self, command):
        """Run a command on the current group.

        Parameters
        ----------
        command : str
            Command to run
        """

        for name, output in self.groups[self.current].run(command).items():
            if len(output) == 0:
                output = ["[no output]"]

            print(
                "  {name} > {output}"
                .format(name=name, output=output[0].strip()))

            for line in output[1:]:
                print(" " * (len(name) + 5) + line.strip())

    def switch_group(self, command):
        """Switch the current group

        Parameters
        ----------
        command : str
            Raw input command
        """

        split = command.split(" ")

        if len(split) < 2:
            print("  [SSHM] No group specified.")

        elif split[1] not in self.groups:
            print(
                "  [SSHM] Specified group {group} does not exist."
                .format(group=split[1]))

        else:
            self.current = split[1]

    def run(self):
        """Run the CLI tool."""

        while True:
            command = input("{group} | ".format(group=self.current))

            if command == "exit":
                self.disconnect()
                break

            elif command.split(" ")[0] == "switch":
                self.switch_group(command)

            else:
                self.exec_command(command)

            print()

        print()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        raise Exception("No config file specified.")

    try:
        cfg = importlib.import_module(sys.argv[1])
    except Exception as e:
        raise Exception(
            "Could not import target config file: " + str(e))

    ManageCLI(cfg).run()
