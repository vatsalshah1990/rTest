__     __    _             _   ____  _           _     
\ \   / /_ _| |_ ___  __ _| | / ___|| |__   __ _| |__  
 \ \ / / _` | __/ __|/ _` | | \___ \| '_ \ / _` | '_ \ 
  \ V / (_| | |_\__ \ (_| | |  ___) | | | | (_| | | | |
   \_/ \__,_|\__|___/\__,_|_| |____/|_| |_|\__,_|_| |_|

ECE-C 433 Independent Project
rTest.py - A remote Testing FrameWork

Documentation

Tested on Python 2.7

Dependencies:

1. Make sure you've the Paramiko library. If you don't, install using:
	sudo pip install Paramiko
	Note: This is a dependency for fabric
2. Make sure you've the PyCrypto library. If you don't, install using:
	sudo pip install PyCrypto
	Note: This is a dependency for fabric
3. Make sure you've the fabric library. If you don't, install using:
	sudo pip install fabric
4. All the other libraries used come default in Python 2.7
5. Needs folder_sync.py in the same directory as rTest.py

Usage: python rTest.py [options] hostnames

rTest.py is a python based remote testing FrameWork. Use this program as your
terminal console while coding in your favorite editor and running tests on any
number of remote machines simultaneously. This program also maintains a sync
between your local project directory and the remote directory so you don't
have to worry about constantly SSH'ing into remote machines and running your
code. Neither do you have to worry about transfering the files constantly
because you have terminal editors. This program else enables you to send email
alerts just in case you want to start a test and want to grab a quick bite.
Your results can be sent to your email.

Options:
  -h, --help            show this help message and exit
  -p PASSWORD, --password=PASSWORD
                        Use this flag to enter the password
  -a, --alert           Use this flag to enable email alerts
  -l LOCAL_FOLDER, --local_folder=LOCAL_FOLDER
                        Enter the local folder path on your machine
  -r REMOTE_FOLDER, --remote_folder=REMOTE_FOLDER
                        Enter the remote path on the hosts where you want to
                        sync

Console commands:

1. alert - Program needs to be run with -a flag for this functionality.
	Now the program will send you an email alert for each output if you prefix the command with 'alert'.
	For e.g.: user@rTest$alert python hello_world.py
	This will run the command 'python hello_world.py' on all the remote hosts and send the output to your email address upon completion.
	Note: The use of -a flag prompts will by default prompt you for your gmail username and password. This is required for sending alerts!
2. sudo - This will run the desired command with superuser access on all the hosts.
	Please make sure that you have sudo access on the hosts before using this command.
	Note: Fabric will prompt you for sudo password if not found in cache
	For e.g.: user@rTest$sudo apt-get install python
	Will install python on all the remote hosts
3. All other commands can be run as on a terminal window.
	For e.g.: user@rTest$cd ~/test
	Will change the current working directory to ~/test on all the remote hosts

Examples:

1. To run existing programs on remote hosts without folder_sync:

	Run -->
	$python rTest.py user@tux.cs.drexel.edu user@xunil.coe.drexel.edu

	Output -->
	***** Welcome to rTest!!! A remote testing FrameWork *****
	[user@tux.cs.drexel.edu] Login password for 'user':
	*****Starting Console*****
	user@rTest$cd test
	user@rTest$python hello_world.py
	[user@tux.cs.drexel.edu] run: python hello_world.py
	[user@tux.cs.drexel.edu] out: Hello World
	[user@tux.cs.drexel.edu] out:

	[user@xunil.coe.drexel.edu] run: python hello_world.py
	[user@xunil.coe.drexel.edu] out: Hello World
	[user@xunil.coe.drexel.edu] out:

2. To run a local project on remote hosts with folder_sync:
	You can continue to edit your code, rename, add/delete files in your project directory. The program will sync the changes to all the remote hosts every 5 seconds. The time period can be changed from within the source code.
	Reminder: Use -a flag to use the alerts

	Run -->
	python rTest.py -l '/Users/xxx/Downloads/test' -r '~/test' user@tux.cs.drexel.edu user@xunil.coe.drexel.edu

	Output -->
	***** Welcome to rTest!!! A remote testing FrameWork *****
	[user@tux.cs.drexel.edu] Login password for 'user':
	Folder Sync started...
	[user@xunil.coe.drexel.edu] run: mkdir -p ~/test
	[user@tux.cs.drexel.edu] run: mkdir -p ~/test
	[user@tux.cs.drexel.edu] put: /Users/xxx/Downloads/test/.DS_Store -> /home/user/test/.DS_Store
	[user@tux.cs.drexel.edu] put: /Users/xxx/Downloads/test/folder_sync.py -> /home/user/test/folder_sync.py
	[user@tux.cs.drexel.edu] put: /Users/xxx/Downloads/test/hello_world.py -> /home/user/test/hello_world.py
	[user@tux.cs.drexel.edu] put: /Users/xxx/Downloads/test/rTest.py -> /home/user/test/rTest.py
	[user@xunil.coe.drexel.edu] put: /Users/xxx/Downloads/test/.DS_Store -> /home/DREXEL/user/test/.DS_Store
	[user@xunil.coe.drexel.edu] put: /Users/xxx/Downloads/test/folder_sync.py -> /home/DREXEL/user/test/folder_sync.py
	[user@xunil.coe.drexel.edu] put: /Users/xxx/Downloads/test/hello_world.py -> /home/DREXEL/user/test/hello_world.py
	[user@xunil.coe.drexel.edu] put: /Users/xxx/Downloads/test/rTest.py -> /home/DREXEL/user/test/rTest.py
	*****Starting Console*****
	user@rTest$

Known Issues:

1. Occasianaly the put method from fabric throws an [I/O, 5 error]
	This is a known 	open issue with fabric caused on various OS including Fedora, Ubuntu, etc.
	Effect on this program: Causes processes to keep running multiple put commands due to unsuccessfull attempts.
	Resolution: Just hit CTRL + C if this happens to you and restart the program. No data is deleted or lost due to the issue.
