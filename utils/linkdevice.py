import subprocess
import shlex


def linkDevice(deviceName: str):
    """
    Generates a QR-code, scan on your device.
    :return: None
    """
    qr_dest = "/tmp/qrcode.png"
    cmd = f'signal-cli link -n "{deviceName}"'
    cmd = shlex.split(cmd)
    print(cmd)
    # We use .Popen() to process output before it finishes.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    result = proc.stdout.readline().decode()
    subprocess.Popen.terminate(proc)
    pub_key = result.split('pub_key=')[1].rstrip()
    cmd = f'qrencode {pub_key} -o {qr_dest}'
    subprocess.run(cmd.split())
    cmd = f"xdg-open {qr_dest}"
    subprocess.run(cmd.split())
    print(f"Remove {qr_dest} when done.")
