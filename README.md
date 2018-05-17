# Python-UartModem-OTAU
This is script for MCU OTAU process presentation. It shows how MCU should behave in order to perform successful application firmware update.
# Installation
 - Install python 3.6
 - Run "pip3 install -r <repo_root>/requirements.txt"
# Run Script
 - Generate MCU OTAU package (please see Silvair OTAU manual)
 - Connect UARTModem to PC (using USB - RS-232 adapter)
 - Update config.json file
 - Run "py -3 main.py -c config.json"
 - Send generated MCU OTAU package using nRF Connect application
