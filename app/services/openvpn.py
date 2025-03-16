import os
import sys
import subprocess
import threading
import time
import signal
import logging
from app.services.logger import get_logger

from app.config import VPN_USER, VPN_PASS

logger = get_logger("vpn_connector")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OVPN_CONFIG_PATH = os.path.join(BASE_DIR, "config.ovpn")
AUTH_FILE_PATH = os.path.join(BASE_DIR, "auth.txt")

if not os.path.exists(OVPN_CONFIG_PATH):
    logger.error("OpenVPN config file not found.")
    sys.exit(1)


def connect_vpn():
    """
    Connects to the VPN using OpenVPN.
    Creates the auth file with credentials, starts the OpenVPN process, and monitors its output.
    Returns the subprocess.Popen object representing the VPN process.
    """
    logger.info("Connecting to VPN...")

    os.makedirs(BASE_DIR, exist_ok=True)

    with open(AUTH_FILE_PATH, "w") as f:
        f.write(f"{VPN_USER}\n{VPN_PASS}")
    os.chmod(AUTH_FILE_PATH, 0o600)

    cmd = ["openvpn", "--config", "config.ovpn",
           "--auth-user-pass", "auth.txt"]
    vpn_process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=BASE_DIR)

    is_connected = False
    connection_event = threading.Event()

    def monitor_stdout():
        nonlocal is_connected
        for line in iter(vpn_process.stdout.readline, ""):
            line = line.strip()
            logger.debug("VPN: %s", line)
            if "Initialization Sequence Completed" in line:
                is_connected = True
                logger.info("VPN connection established.")
                connection_event.set()
                break

    def monitor_stderr():
        for line in iter(vpn_process.stderr.readline, ""):
            line = line.strip()
            logger.error("VPN Error: %s", line)

    stdout_thread = threading.Thread(target=monitor_stdout, daemon=True)
    stderr_thread = threading.Thread(target=monitor_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    timeout = 60  # seconds
    if not connection_event.wait(timeout):
        try:
            os.remove(AUTH_FILE_PATH)
        except Exception as e:
            logger.warning("Failed to remove auth file: %s", str(e))
        logger.error("Failed to establish VPN connection within timeout.")
        raise RuntimeError("Failed to establish VPN connection.")

    try:
        os.remove(AUTH_FILE_PATH)
    except Exception as e:
        logger.warning("Failed to remove auth file: %s", str(e))

    return vpn_process


def disconnect_vpn(vpn_process):
    """
    Disconnects the VPN by sending a SIGINT signal to the VPN process.
    """
    logger.info("Disconnecting from VPN...")
    vpn_process.send_signal(signal.SIGINT)


def ensure_vpn_connection():
    """
    Ensures that the VPN connection is maintained.
    If the connection drops, it attempts to reconnect.
    This function loops indefinitely.
    """
    vpn_process = None
    while True:
        try:
            vpn_process = connect_vpn()
            while True:
                retcode = vpn_process.poll()
                if retcode is not None:
                    logger.warning(
                        "VPN process terminated with code %s. Reconnecting...", retcode)
                    break
                time.sleep(5)
        except Exception as e:
            logger.error("Error connecting to VPN: %s", str(e))
        logger.info("Attempting to reconnect to VPN in 10 seconds...")
        time.sleep(10)
