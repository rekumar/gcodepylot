import serial.tools.list_ports as lp
import sys
from typing import Any, Dict


def which_os():
    if sys.platform.startswith("win"):
        return "Windows"
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        return "Linux"
    else:
        raise EnvironmentError("Unsupported platform")


def _get_port_windows(device_identifiers:Dict[str, Any]) -> str:
    """Given a dictionary of pyserial device identifiers, returns the port name

    Args:
        device_identifiers (Dict): Dictionary of pyserial device identifiers (e.g. vid, pid, serial_number)

    Raises:
        ValueError: No matching port found

    Returns:
        str: Name of the port to connect to this device
    """
    for p in lp.comports():
        match = True
        for attr, value in device_identifiers.items():
            if getattr(p, attr) != value:
                match = False
        if match:
            return p.device
    raise ValueError("Cannot find a matching port!")


def _get_port_linux(serial_number: str) -> str:
    """
    finds port number for a given hardware serial number
    """
    for p in lp.comports():
        if p.serial_number and p.serial_number == serial_number:
            return p.device
    raise ValueError("Cannot find a matching port!")


def get_port(device_identifiers):
    operatingsystem = which_os()
    if operatingsystem == "Windows":
        port = _get_port_windows(device_identifiers)
    elif operatingsystem == "Linux":
        port = _get_port_linux(device_identifiers["serialid"])
    return port
