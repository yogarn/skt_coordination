from kazoo.client import KazooClient
import threading, time

def worker(worker_id):
    zk = KazooClient(hosts='localhost:2181')
    zk.start()

    path = zk.create("/lock/node-", ephemeral=True, sequence=True)
    print(f"[Worker-{worker_id}] Node dibuat: {path}")

    while True:
        children = zk.get_children("/lock")
        children.sort()

        my_node = path.split("/")[-1]

        if my_node == children[0]:
            print(f"[Worker-{worker_id}] Masuk CR")
            time.sleep(2)
            print(f"[Worker-{worker_id}] Keluar CR")
            zk.delete(path)
            break
        else:
            prev_index = children.index(my_node) - 1
            prev_node = children[prev_index]

            event = threading.Event()

            def watcher(event_data):
                event.set()

            zk.exists(f"/lock/{prev_node}", watch=watcher)
            event.wait()

    zk.stop()

# setup root
zk = KazooClient(hosts='localhost:2181')
zk.start()
if not zk.exists("/lock"):
    zk.create("/lock")
zk.stop()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
