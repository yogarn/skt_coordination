# lab4_vector_clock.py
class VectorClock:
	def __init__(self, pid, all_pids):
		self.pid = pid
		self.clock = {p: 0 for p in all_pids}

	def tick(self):
		self.clock[self.pid] += 1
		return dict(self.clock)

	def send(self):
		self.clock[self.pid] += 1
		return dict(self.clock)

	def receive(self, remote_ts):
		for p in self.clock:
			self.clock[p] = max(self.clock[p], remote_ts[p])
		self.clock[self.pid] += 1  # increment setelah merge

	def happens_before(self, ts_a, ts_b) -> bool:
		"""Return True jika ts_a causally precedes ts_b."""
		leq = all(ts_a[p] <= ts_b[p] for p in ts_a)
		lt = any(ts_a[p] < ts_b[p] for p in ts_a)
		return leq and lt

	def concurrent(self, ts_a, ts_b) -> bool:
		return (not self.happens_before(ts_a, ts_b) and
				not self.happens_before(ts_b, ts_a))

# Demo
pids = ["P1", "P2", "P3"]
vc1 = VectorClock("P1", pids)
vc2 = VectorClock("P2", pids)
vc3 = VectorClock("P3", pids)

ts_a = vc1.send()  # P1 sends
vc2.receive(ts_a)
ts_b = vc2.send()  # P2 sends after receiving

print("ts_a:", ts_a)
print("ts_b:", ts_b)
print("a → b?", vc1.happens_before(ts_a, ts_b))  # True
print("b → a?", vc1.happens_before(ts_b, ts_a))   # False
print("concurrent?", vc1.concurrent(ts_a, ts_b))    # False (a→b, bukan concurrent)

# Skenario concurrent: P1 dan P3 kirim pesan secara bersamaan ke P2
vc3 = VectorClock("P3", pids)
ts_c = vc3.send()    # P3 kirim tanpa tahu tentang ts_a
print("\nts_a (dari P1):", ts_a)
print("ts_c (dari P3):", ts_c)
print("a → c?", vc1.happens_before(ts_a, ts_c))   # False
print("c → a?", vc1.happens_before(ts_c, ts_a))   # False
print("a || c (concurrent)?", vc1.concurrent(ts_a, ts_c))  # True!

# Skenario baru: P2 dan P3 mengirim ke P1 secara bersamaan
pids = ["P1", "P2", "P3"]
vc1 = VectorClock("P1", pids)
vc2 = VectorClock("P2", pids)
vc3 = VectorClock("P3", pids)

# Dua event send tanpa saling mengetahui -> concurrent
ts_p2 = vc2.send()  # P2 -> P1
ts_p3 = vc3.send()  # P3 -> P1

print("\nts_p2 (send dari P2):", ts_p2)
print("ts_p3 (send dari P3):", ts_p3)
print("p2 || p3 (concurrent)?", vc1.concurrent(ts_p2, ts_p3))

# P1 menerima kedua pesan (urutan terima bisa bervariasi)
vc1.receive(ts_p2)
print("Clock P1 setelah receive dari P2:", vc1.clock)
vc1.receive(ts_p3)
print("Clock P1 setelah receive dari P3:", vc1.clock)
