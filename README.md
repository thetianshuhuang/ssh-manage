# SSH Manage

Programmatically manage multiple devices over SSH

## Usage - Command line tool

Add your device definitions to ```settings.py```. Each device should be a dictionary with entries ```name```, ```ip```, ```user```, and ```pw```:

```python
{
	"name": "example",
	"ip": "192.168.0.105",
	"user": "pi",
	"pw": "hunter2"
}
```

Then, run ```python manage.py```.

## Example session
```
[SSHM] 2 devices connected.

SSH Group | echo '{name}'
device_1 > device_1

device_2 > device_2

SSH Group | cd ~; ls
device_1 > [no output]

device_2 > test_folder
           secrets.txt
           test_file.py

SSH Group | touch {name}.txt
device_1 > [no output]

device_2 > [no output]

SSH Group | ls
device_1 > device_1.txt

device_2 > device_2.txt

SSH Group | cd ~/test_folder; ls
device_1 > bash: cd: test_folder: No such file or directory

device_2 > a.out
           program.c

SSH Group | exit

[SSHM] 2 devices disconnected.

```
