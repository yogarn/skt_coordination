import threading, queue, time, random

class Process(threading.Thread):
	def __init__(self, pid, peers, pids):
		super().__init__(daemon=True)
		self.pid = pid
		self.pids = pids
		self.clock = {proc_id: 0 for proc_id in pids}
		self.inbox = queue.Queue()
		self.peers = peers  # dict: pid -> Process

	def _tick(self):
		self.clock[self.pid] += 1

	def send(self, target_pid, message):
		self._tick()
		vc = self.clock.copy()
		print(f" [{self.pid}|vc={vc}] SEND '{message}' → {target_pid}")
		self.peers[target_pid].inbox.put((vc, self.pid, message))

	def receive(self):
		incoming_vc, sender, msg = self.inbox.get()
		for proc_id in self.pids:
			self.clock[proc_id] = max(self.clock[proc_id], incoming_vc[proc_id])
		self._tick()
		print(f" [{self.pid}|vc={self.clock}] RECV '{msg}' ← {sender}")

	def local_event(self, name):
		self._tick()
		print(f" [{self.pid}|vc={self.clock}] EVENT '{name}'")

	def run(self):
		time.sleep(random.uniform(0, 0.2))
		if self.pid == "P1":
			self.local_event("start")
			self.send("P2", "hello")
			self.receive()  # will get from P2
		elif self.pid == "P2":
			self.receive()  # dari P1
			self.local_event("process")
			self.send("P1", "ack")
			self.send("P3", "data")
		elif self.pid == "P3":
			self.receive()  # dari P2
			self.send("P4", "forward")
			self.local_event("done")
		elif self.pid == "P4":
			self.receive()  # dari P3
			self.local_event("received")

pids = ["P1", "P2", "P3", "P4"]
processes = {}
for pid in pids:
	processes[pid] = Process(pid, processes, pids)

print("=== Jalankan simulasi Vector Clock ===")
for p in processes.values():
	p.start()
for p in processes.values():
	p.join(timeout=3)
print("=== Selesai ===")
