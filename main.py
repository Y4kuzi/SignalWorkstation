import subprocess  # https://docs.python.org/3/library/subprocess.html
import shlex
import threading
import os
import config
import time
import signal  # Not related to the messaging app.
from fcntl import fcntl, F_GETFL, F_SETFL

from utils import linkDevice, SignalListener


# apt install signal-cli qrencode
# Conf stored in $HOME/.local/share/signal-cli/data/
# https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc

# Link your device: call the function `linkDevice(<devicename>: str)` at the bottom of the file.


class SignalDaemon(threading.Thread):
    def __init__(self, username):
        self.username = username
        self.signal_process = None
        self.listener = None
        for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, self.close_process)
        threading.Thread.__init__(self)

    def run(self):
        if self.daemonize():
            print("[+] Signal running as daemon.")
            print(f"[+] Username: {self.username}")

    def daemonize(self) -> bool:
        cmd = f"signal-cli -u {self.username} daemon"
        self.signal_process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Set os.O_NONBLOCK flag:
        # http://eyalarubas.com/python-subproc-nonblock.html

        # Retrieve current flags.
        flags = fcntl(self.signal_process.stdout, F_GETFL)

        # Append os.O_NONBLOCK to flags.
        fcntl(self.signal_process.stdout, F_SETFL, flags | os.O_NONBLOCK)

        self.listener = SignalListener()
        self.listener.hook(self.signal_process)
        self.listener.start()
        time.sleep(0.1)
        return True

    def sendMessage(self, text: str, recipient: str):
        self.callBack(f'send -m "{text}" {recipient}')

    def linkedDevices(self):
        self.callBack("listDevices")

    def close_process(self, *args):
        print(f"Caught exit signal: {args}")
        self.listener.active = False
        subprocess.Popen.terminate(self.signal_process)
        print("Main process closed.")

    @staticmethod
    def callBack(data: str) -> subprocess:
        """
        Sends data to signal-cli and returns CopmletedProcess instance:
        https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess
        Output is stored in the `stdout` property.
        :param data: cli commands
        :return: CompletedProcess instance
        """
        print(f"[<] Sending: {data}")
        cmd = f"signal-cli --dbus {data}"
        cmd = shlex.split(cmd)
        comp_proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[>] {comp_proc}")
        return comp_proc


Signal = SignalDaemon(config.USERNAME)
Signal.start()

# linkDevice("Your device name")
