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

import settings
from device import make_group


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


def manage():
    """Run command line tool"""

    _splash()

    group = make_group(settings.DEVICES)

    print("[SSHM] {n} devices connected.".format(n=len(group)))

    while True:
        command = input("SSH Group | ")

        if command == "exit":
            group.disconnect()
            print("\n[SSHM] {n} devices disconnected.\n".format(n=len(group)))
            break

        for name, output in group.run(command).items():

            if len(output) == 0:
                output = ["[no output]"]

            print(
                "{name} > {output}"
                .format(name=name, output=output[0].strip()))

            for line in output[1:]:
                print(" " * (len(name) + 3) + line.strip())

            print()


if __name__ == "__main__":

    manage()
