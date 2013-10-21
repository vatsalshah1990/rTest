# Vatsal Shah
# ECE-C 433 Independent Project

# rTest.py is a python based remote testing FrameWork
# Use this program as your terminal console while coding in
# your favorite editor and running tests on any number of remote
# machines simultaneously. This program also maintains a sync between
# your local project directory and the remote directory so you don't
# have to worry about constantly SSH'ing into remote machines and
# running your code. Neither do you have to worry about transfering the
# files constantly because you have terminal editors. This program else
# enables you to send email alerts just in case you want to start a test
# and want to grab a quick bite. Your results can be sent to your email.

# Python 2.7 Default libraries
from __future__ import with_statement
import optparse
import sys
import os
import time
import multiprocessing
import smtplib
import getpass
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formatdate

# Install using sudo pip install fabric
# Not a part of default library
from fabric.api import show, hide, run, get, put, env, execute, cd, local, sudo
from fabric.network import disconnect_all

# Global Flag to Turn Alerts On/Off due to errors
alert_flag = False

# Method used to get user password for the host in case -p flag is not used


def hostname_check():
    run("hostname")

# Method to run commands on remote hosts


def remote_command(cmd):
    def go():
        with show('running', 'stdout', 'stderr'):
            out = run(cmd)
        return out
    with hide('running'):
        out = execute(go)
    return out

# Method to run sudo commands on remote hosts
# May prompt for sudo password if not in cache
# Note: Make sure you've sudo access to the host before using this


def sudo_command():
    def go():
        with show('running', 'stdout', 'stderr'):
            out = sudo(cmd)
        return out
    with hide('running'):
        out = execute(go)
    return out

# Method to run commands on localhost


def local_command(cmd):
    def go():
        with show('stdout'):
            out = local(cmd)
    with hide('running'):
        out = execute(go)
    return out

# Runs the folder_sync.py program in background for the remote hosts
# Multiprocessing - Each process maintains one host


def folder_sync(host):
    with hide('warnings', 'running'):
        local_command('python folder_sync.py -l' + local_folder + ' -r' + remote_folder + ' -p' + env.password + ' ' + host)

# Method used to send email alerts with the output to the user


def send_alert(output, username, password):
    msg = MIMEMultipart()
    fromaddr = 'alert@rTest.com'
    toaddrs = username + '@gmail.com'
    msg["From"] = fromaddr
    msg["To"] = toaddrs
    msg["Subject"] = "rTest Alert"
    msg['Date'] = formatdate(localtime=True)
    body = "Your output is ready to view:\n %s" % output
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.close()
    except smtplib.SMTPException as err:
        print "Alert module failed"
        print str(err)
        # Sets this flag is an error occurs so that no further alert calls
        # are made. Program will ignore even if the user prompts for alert
        alert_flag = True
        pass


def main():
    # Using parser library for handling remote_command line arguments
    usage = "usage: python rTest.py [options] hostnames"
    prog_desc = """rTest.py is a python based remote testing FrameWork. Use this program as your terminal console while coding in your favorite editor and running tests on any number of remote machines simultaneously. This program also maintains a sync between your local project directory and the remote directory so you don't have to worry about constantly SSH'ing into remote machines and running your code. Neither do you have to worry about transfering the files constantly because you have terminal editors. This program else enables you to send email alerts just in case you want to start a test and want to grab a quick bite. Your results can be sent to your email."""
    parser = optparse.OptionParser(usage=usage, description=prog_desc)
    parser.add_option(
        '-p', '--password', help="Use this flag to enter the password", dest='password', action='store')
    parser.add_option(
        '-a', '--alert', help="Use this flag to enable email alerts", dest='alert', default=False, action='store_true')
    parser.add_option(
        '-l', '--local_folder', help='Enter the local folder path on your machine',
        dest='local_folder', action='store')
    parser.add_option(
        '-r', '--remote_folder', help='Enter the remote path on the hosts where you want to sync',
        dest='remote_folder', action='store')
    (opts, args) = parser.parse_args()
    global local_folder
    global remote_folder

    # Defaults to home directory
    local_folder = '~'
    remote_folder = '~'

    try:
        print "***** Welcome to rTest!!! A remote testing FrameWork *****"

        # Fabric Environment Settings
        env.hosts = args
        env.keepalive = True
        env.skip_bad_hosts = True
        env.warn_only = True

        # List of all the processes created for folder_sync
        sync_process = []

        # Checks if user wanted the alert option
        if opts.alert:
            print "^^^You've turned on email alerts, please enter your Gmail credentials^^^"
            alert_username = raw_input("Enter username:")
            alert_password = getpass.getpass()

        # Checks if user provided the remote host password
        # If not Fabric will prompt the user on run
        # Program runs the hostname_check method to cache the password
        if opts.password != None:
            env.password = opts.password
        else:
            with hide('running', 'stdout', 'stderr'):
                execute(hostname_check)

        # Both local and remote folder paths need to be provided for folder_sync functionality
        if opts.local_folder != None and opts.remote_folder != None:
            local_folder = opts.local_folder.strip("'")
            remote_folder = opts.remote_folder.strip("'")
            print "Folder Sync started..."

            # Creates as many processes as the hosts and runs folder_sync
            for host in env.hosts:
                sync_process.append(multiprocessing.Process(target=folder_sync, args=(host,)))

            for process in sync_process:
                process.daemon = True
                process.start()

        # Waits for initial sync
        # Increase the time if working with large number of files
        time.sleep(len(sync_process) * 6)
        out = ''
        print "*****Starting Console*****"

        # Changes the default directory to remote path
        current_dir = remote_folder

        # Flag used to catch alert prompts by the user
        a_flag = False

        while True:
            with cd(current_dir):
                cmd = raw_input(env.user + '@rTest$')
                if cmd == 'quit()' or cmd == 'exit()':
                    for process in sync_process:
                        # Terminates all the folder_sync processes
                        process.terminate()
                    # Closes all the SSH connections
                    disconnect_all()
                    time.sleep(3)
                    break
                if cmd.startswith('alert'):
                    cmd = cmd.rsplit('alert ')[1]
                    a_flag = True
                if cmd.startswith('cd'):
                    current_dir = cmd.split()[1]
                elif cmd.startswith('sudo'):
                    out = sudo_command(cmd)
                else:
                    out = remote_command(cmd)
            if opts.alert and a_flag and not alert_flag and out != '':
                send_alert(out, alert_username, alert_password)
                out = ''
                a_flag = False
    except KeyboardInterrupt:
        print "\nrTest shutdown"
        # Terminates all the processes created
        for process in sync_process:
            process.terminate()
        # Closes all the SSH connections
        disconnect_all()
        time.sleep(3)
        exit()

if __name__ == "__main__":
    main()
