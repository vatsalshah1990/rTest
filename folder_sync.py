# Vatsal Shah
# ECE-C 433 Independent Project

# Folder Sync provides remote server syncing functionality for rCode

from __future__ import with_statement
import optparse
import sys
import os
from fabric.api import show, hide, run, get, put, env, execute, cd, hosts
from fabric.network import disconnect_all
import time

# Keeps a track of monitored files and folders in previous run
monitored_files = {}
monitered_folders = []

# A simple class to keep track of each file being monitored


class file_track:
    'Keeps track of the modification time of a file.'
    def __init__(self, filename):
        self.filename = filename
        self.date_modified = os.stat(self.filename).st_mtime
        self.has_changed()

    # Checks the date_modified attribute of the file
    def has_changed(self):
        date_modified = os.stat(self.filename).st_mtime
        if date_modified == self.date_modified:
            return False
        else:
            self.date_modified = date_modified
            return True

# Runs a command on the remote host


def remote_command(cmd):
    def go():
        with show('running', 'stdout', 'stderr'):
            run(cmd)
    with hide('running'):
        execute(go)

# Method to maintain folder sync between local folder and remote folder


def folder_sync():
    # Lists to keep a track of the current state of the directory
    current_paths = []
    current_dirs = []

    with show('running'):
        # Gets a tuple of all the file, folders & subfolders in a directory
        for dirpath, dirnames, filenames in os.walk(local_folder):
            # Keep a copy of current folder path in the list
            current_dirs.append(dirpath)

            # If a folder was not found in the monitored folders,
            # It creates a new folder on the remote host and adds
            # to the list of monitored folders
            if dirpath not in monitered_folders:
                remotepath = remote_folder + dirpath.rsplit(local_folder, 1)[1]
                cmd = 'mkdir -p ' + remotepath
                remote_command(cmd)
                monitered_folders.append(dirpath)

            for filename in filenames:
                localpath = os.path.join(dirpath, filename)
                current_paths.append(localpath)
                remotepath = remote_folder + localpath.rsplit(local_folder, 1)[1]
                # If a file has been updated since previous state,
                # It uploads a new copy to the host
                if localpath in monitored_files:
                    if monitored_files[localpath].has_changed():
                        put(localpath, remotepath)
                # If the file wasn't found in the monitored files,
                # It uploads the new file and adds to the list
                else:
                    monitored_files[localpath] = file_track(localpath)
                    put(localpath, remotepath)

        # Checks if a file was deleted
        # If the file is not found in the current run and the dictionary has the key,
        # It deleted the file from the host and them removes the entry
        for file_path in monitored_files.keys():
            if file_path not in current_paths:
                cmd = 'rm -f ' + remote_folder + file_path.rsplit(local_folder, 1)[1]
                remote_command(cmd)
                del monitored_files[file_path]

        # Checks if a folder was deleted
        # If the folder is not found in the current run of the local directory and
        # the monitored folders has an entry,
        # It deletes the folder from the host and then removes the entry
        for dirpath in monitered_folders:
            if dirpath not in current_dirs:
                cmd = 'rm -r ' + remote_folder + dirpath.rsplit(local_folder, 1)[1]
                remote_command(cmd)
                monitered_folders.remove(dirpath)

# Task to call folder_sync method


def folder_sync_run():
    while True:
        try:
            with hide('running'):
                execute(folder_sync)
                # Frequency of syncing with the remote hosts
                time.sleep(5)
        except Exception, e:
            print "Ending folder sync unexpectedly"
            print e
            # Closing all the SSH connections
            disconnect_all()
            exit()


def main():
    # Using parser library for handling remote_command line arguments
    prog_desc = """Folder Sync Functionality for rCode"""
    parser = optparse.OptionParser(description=prog_desc)
    parser.add_option(
        '-p', '--password', help="Use this flag to enter the password", dest='password', action='store')
    parser.add_option(
        '-l', '--local_folder', help='Enter the local folder path on your machine',
        dest='local_folder', action='store')
    parser.add_option(
        '-r', '--remote_folder', help='Enter the remote path on the hosts where you want to sync',
        dest='remote_folder', action='store')
    (opts, args) = parser.parse_args()
    global local_folder
    global remote_folder

    try:

        # Fabric Environment Settings
        env.hosts = args
        env.keepalive = True
        env.skip_bad_hosts = True
        env.warn_only = True

        # Sets the password if the parent program provided the entry
        if opts.password != None:
            env.password = opts.password

        if opts.local_folder != None and opts.remote_folder != None:
            local_folder = opts.local_folder.strip("'")
            remote_folder = opts.remote_folder.strip("'")

            folder_sync_run()

    except KeyboardInterrupt:
        print "\nFolder Sync Ended for %s" % (env.hosts)
        # Closes all the SSH connections
        disconnect_all()

if __name__ == "__main__":
    main()
