import select
import threading


class SignalListener(threading.Thread):
    def __init__(self):
        self.processes = []
        self.active = True
        threading.Thread.__init__(self)

    def run(self):
        print("Listener activated...")

        while self.active:
            read, write, error = select.select([proc.stdout for proc in self.processes], [], [proc.stderr for proc in self.processes], 1.0)
            for proc in read:
                proc = next((p for p in self.processes if p.stdout == proc), None)
                recv = proc.stdout.readline()
                if not recv:
                    print(f"No data received from: {proc}")
                    self.quit(proc)
                    continue
                print(f"New data: {recv}")

            for proc in error:
                proc = next((p for p in self.processes if p.stderr == proc), None)
                recv = proc.stderr.readline()
                print(f"Error: {recv}")
                self.quit(proc)

        print("Listener stopped.")

    def hook(self, proc):
        self.processes.append(proc)
        print(f"New process hooked for listening: {proc}")

    def quit(self, proc):
        self.processes.remove(proc)
        print(f"Process unhooked: {proc}")
