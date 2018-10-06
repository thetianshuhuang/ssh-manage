"""
"""

import settings
from device import make_group


AUTHOR = "Tianshu Huang"
DATE = "Fall 2018"


def _splash():
    """???"""

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

    _splash()

    group = make_group(settings.DEVICES)

    while True:
        command = input("SSH Group | ")

        if command == "exit":
            group.disconnect()
            break

        for name, output in group.run(command).items():

            if len(output) == 0:
                output = ["[No output]"]

            print(
                "{name} > {output}"
                .format(name=name, output=output[0].strip()))

            for line in output[1:]:
                print(" " * (len(name) + 3) + line.strip())

            print()


if __name__ == "__main__":

    manage()
