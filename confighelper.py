import os
import configparser

if os.name == 'nt': # Windows
    directory = os.getenv('LOCALAPPDATA') + "/ZMasterPrint/config/"

else: # Linux and MacOS
    directory = os.path.expanduser("~") + "/.config/ZMasterPrint/"

local_file = directory + "/config.ini"

def write_config_file(host, printer, label_height, label_width, top_margin, left_margin):
    config_file = configparser.ConfigParser()
    config_file.add_section("Device")
    config_file.set("Device", "host", host)
    config_file.set("Device", "printer", printer)
    config_file.add_section("Label")
    config_file.set("Label", "width", label_width)
    config_file.set("Label", "height", label_height)
    config_file.set("Label", "top_margin", top_margin)
    config_file.set("Label", "left_margin", left_margin)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(local_file, 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()

def read_config_file():
    config = configparser.ConfigParser()
    config.read(local_file)
    return config


