import etcd3, threading, time


def watch_key(etcd, key):
	"""Watch sebuah key dan print setiap perubahan."""
	print(f"Watching key: {key.decode()}")
	events_iterator, _cancel = etcd.watch(key)
	for event in events_iterator:
		print(
			f" Event: {type(event).__name__} | "
			f"key={event.key.decode()} | "
			f"value={event.value.decode() if event.value else 'deleted'}"
		)


def campaign_node(node_name, leader_key, start_barrier, first_winner, lock, output_log):
	"""Campaign leader election via transaksi atomik etcd (compare-and-swap)."""
	client = etcd3.client(host='localhost', port=2379)
	lease = client.lease(5)

	start_barrier.wait()
	output_log.append(f"{node_name} mulai campaign")

	won, _responses = client.transaction(
		compare=[client.transactions.version(leader_key) == 0],
		success=[client.transactions.put(leader_key, node_name, lease)],
		failure=[],
	)

	if won:
		with lock:
			if first_winner["name"] is None:
				first_winner["name"] = node_name
				output_log.append(f"{node_name} menang pertama")
				print(f"{node_name} menjadi leader pertama")
			else:
				output_log.append(f"{node_name} menjadi leader")
				print(f"{node_name} menjadi leader")
		time.sleep(1)
		lease.revoke()
		output_log.append(f"{node_name} resign")
	else:
		leader_value, _metadata = client.get(leader_key)
		current_leader = leader_value.decode() if leader_value else "unknown"
		output_log.append(f"{node_name} kalah, leader saat ini: {current_leader}")
		print(f"{node_name} kalah campaign, leader: {current_leader}")
		lease.revoke()

	client.close()


etcd = etcd3.client(host='localhost', port=2379)

# Start 2 watcher in parallel
watcher_threads = [
	threading.Thread(target=watch_key, args=(etcd, b'/config/threshold'), daemon=True),
	threading.Thread(target=watch_key, args=(etcd, b'/config/timeout'), daemon=True),
]
for watcher_thread in watcher_threads:
	watcher_thread.start()

# Simulate config updates
time.sleep(0.5)
for i in range(5):
	threshold_value = f"threshold={80 + i}"
	timeout_value = f"timeout={30 + i}"
	etcd.put('/config/threshold', threshold_value)
	etcd.put('/config/timeout', timeout_value)
	print(f"Updated: {threshold_value} | {timeout_value}")
	time.sleep(1)

# Leader election with 2 different nodes campaigning simultaneously
print("\n--- Leader Election (2 Nodes, Simultaneous Campaign) ---")
leader_key = '/election/my-service/leader'
etcd.delete(leader_key)
start_barrier = threading.Barrier(2)
first_winner = {"name": None}
winner_lock = threading.Lock()
output_log = []

node_threads = [
	threading.Thread(
		target=campaign_node,
		args=("node-1", leader_key, start_barrier, first_winner, winner_lock, output_log),
	),
	threading.Thread(
		target=campaign_node,
		args=("node-2", leader_key, start_barrier, first_winner, winner_lock, output_log),
	),
]

for thread in node_threads:
	thread.start()
for thread in node_threads:
	thread.join()

print("\n--- Catatan Output ---")
for item in output_log:
	print(f"- {item}")
