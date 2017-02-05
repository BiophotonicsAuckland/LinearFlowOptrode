#!/bin/bash

# Script that runs python microscope client, with a GUI.
# Ensure that this file has been given executable privileges.
# Execture this script AFTER executing run-server.sh

# Run client
echo -e "\n  This is the Raspberry Pi microscope client."
echo -e "  If it isn't loading, make sure you're connected to PiNet, "
echo -e "  and that the server has been launched.\n\n"

python "${PWD}/cameraClientGUI.py"

# Keep terminal open after closing microscope
$SHELL

