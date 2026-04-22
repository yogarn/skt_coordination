Tugas Koordinasi SKT - A  
Nama: **Yoga Raditya Nala**  
NIM: **235150201111020**  

Link GitHub: https://github.com/yogarn/skt_coordination  

## Lab 1 – Simulasi Lamport Clock

1. Jalankan kode lab1_lamport.py, amati output
![image](https://hackmd.io/_uploads/H1Nv0gIpZg.png)
2. Gambar diagram event timeline P1, P2, P3 dengan timestamp-nya
![skt-lamport-diagram](https://hackmd.io/_uploads/SJyz0eI6-g.jpg)
3. Jawab 4 pertanyaan di slide berikutnya secara tertulis
    1. Apakah t(SEND) selalu lebih kecil dari t(RECV)? Mengapa?
**Ya, selalu, karena dalam lamport clock, saat SEND data yang kemudian di RECV, clock di set ke `max(local_clock, t_send) + 1`. Artinya, nilai t(RECV) selalu lebih tinggi 1 daripada t(SEND).**
    2. Apakah bisa disimpulkan P1.start terjadi sebelum P3.done? Jelaskan dengan relasi happened-before!
**Sebenarnya tidak cukup untuk hanya menggunakan timestamp, karena aturan lamport clock menjamin bahwa jika A -> B; maka t(A) < t(B), tetapi bukan berarti sebaliknya selalu benar. Namun di kasus ini, memang terdapat hubungan happened before dari P1.start hingga P3.done melalui comunication chain, sehingga dapat disimpulkan bahwa P1.start terjadi sebelum P3.done.**
    3. Jika P2 crash setelah mengirim 'ack' ke P1 tapi sebelum 'data' ke P3 — apa yang terjadi pada clock P3?
**Jika P2 crash sebelum kirim data ke P3, maka P3 tidak pernah receive data, akibatnya clock di P3 tidak pernah update dari P2, dan clock dari P3 tetap di nilai awal, sehingga bisa jadi event done tidak terjadi atau stuck selamanya.**
    4. Modifikasi kode: ganti LamportClock dengan VectorClock. Tunjukkan hasilnya!
![image](https://hackmd.io/_uploads/H1qMcW86Zx.png)
5. Tambahkan proses P4, kirim pesan dari P3 ke P4 — catat hasilnya
![image](https://hackmd.io/_uploads/B1ImyfIpbx.png)
![image](https://hackmd.io/_uploads/rJsKkz8Tbg.png)

## Lab 2 – ZooKeeper CLI Praktikum
1. Jalankan ZooKeeper via Docker, masuk ke zkCli.sh
```# Jalankan ZooKeeper
docker run -d --name zk \
-p 2181:2181 \
zookeeper:3.9

# Masuk ke CLI
docker exec -it zk ./bin/zkCli.sh
```
![image](https://hackmd.io/_uploads/rJYpyNL6Wl.png)
2. Buat ZNode /mahasiswa/[NIM], isi dengan nama Anda
![image](https://hackmd.io/_uploads/B1G6gE8abl.png)
![image](https://hackmd.io/_uploads/S1vpl48T-g.png)
3. Buka 2 terminal: satu watch /mahasiswa/[NIM], satu lagi ubah nilainya — screenshot notifikasi!
![image](https://hackmd.io/_uploads/SyyZZELTWg.png)
![image](https://hackmd.io/_uploads/By4WWE8TZx.png)
Dapat dilihat di atas, terdapat notifikasi setelah nilai di terminal satu di set ulang.
**4. Buat ephemeral node, lalu tutup koneksi. Buktikan node hilang!**
![image](https://hackmd.io/_uploads/BJYEbEI6-x.png)
![image](https://hackmd.io/_uploads/HyhrZEUTbx.png)
**Dapat dilihat di atas, setelah quit dan masuk lagi, node ephemeral akan hilang karena sifatnya temporary.**

## Lab 2 – ZooKeeper: Distributed Lock (Tugas Inti)
1. Jalankan kode di atas, amati urutan output — apakah hanya 1 worker di CR?
![image](https://hackmd.io/_uploads/HyluQVUTWl.png)
**Ya benar, dari output bisa dilihat hanya ada satu worker yang ada di critical section (CR), tidak ada overlap, hal itu karena kazoo lock yang menggunakan zookeeper dan ephemeral sequential node yang menjamin mutual exclusion. Selama satu worker pegang lock, yang lain cuma bisa menunggu worker tersebut selesai, sehingga akan bergantian satu-persatu.**
2. Ubah jumlah worker menjadi 5. Apakah urutan selalu sama? Mengapa?
![image](https://hackmd.io/_uploads/BJe2N4IpWl.png)
![image](https://hackmd.io/_uploads/HJwa4NITbx.png)
**Dari hasil kedua screenshot di atas, dapat disimpulkan kalau hasilnya tidak selalu sama, pada screenshot pertama, worker 0 acquire lock pertama, sedangkan screenshot kedua, worker 3 berhasil acquire lock pertama. Hal ini dikarenakan thread start tidak deterministik, scheduling OS yang juga tidak deterministik, dan juga networking timing dari zookeper yang juga tidak deterministik, sementara urutan masuk CR tetap secara sequential.**
3. Simulasikan worker yang crash di tengah critical section (tambahkan raise Exception di dalam with lock). Apa yang terjadi pada worker lain?
![image](https://hackmd.io/_uploads/Sy5MU4I6Wg.png)
**Dalam screenshot di atas, saya ubah kode supaya raise exception untuk worker 0. Dapat dilihat ketika terjadi crash pada salah satu worker yang sedang pegang lock, worker lain dapat terus berjalan. Hal tersebut karena lock yang digunakan berbasis ephemeral node. Ketika worker mati, session hilang, dan node dihapus. Lock otomatis dilepas dan dihandover ke node lain, sehingga proses bisa tetap jalan.**
4. Ganti Lock dengan implementasi manual menggunakan ephemeral sequential node. Hint: gunakan pola /lock/node- + cek sibling terkecil
![image](https://hackmd.io/_uploads/rJw9w4Lpbl.png)
**Dalam kode di atas, saya membuat implementasi manual dari kazoo lock yang sudah dibuat abstraksi sebelumnya. Caranya adalah dengan membuat node sequential secara ephemeral, lalu menentukan siapa yang paling kecil, lalu menunggu node sebelumnya (yang lebih kecil) lewat watcher. Hasilnya tetap sama, mutual exclusion tetap terjaga.**

## Lab 3 – Observasi Raft Consensus
1. Buka browser ke https://raft.github.io/
![image](https://hackmd.io/_uploads/S1K0K4Lp-l.png)

2. Tunggu hingga leader terpilih — catat berapa lama (term berapa?)
![image](https://hackmd.io/_uploads/SJTFpNIaWe.png)
**Leader terpilih yaitu S2 setelah 0.147s dan pada term ke-2.**
3. Klik Stop pada leader → amati re-election. Screenshot!
![image](https://hackmd.io/_uploads/ByXU0VU6be.png)
![image](https://hackmd.io/_uploads/B1jwANUp-e.png)
**Ketika leader terpilih timeout atau mati dan tidak mengirimkan heartbeat, maka node lain akan menjadi candidate dan melakukan voting ulang. Dalam hal ini, S4 menjadi leader selanjutnya, dan term naik jadi term 3.**
4. Kirim beberapa log entry via tombol Request — amati replikasi ke follower
![image](https://hackmd.io/_uploads/Sk2iR4L6Zg.png)
![image](https://hackmd.io/_uploads/r1k6CVLTbl.png)
![image](https://hackmd.io/_uploads/H1_aRN8aZg.png)
**Dapat dilihat, ketika ada entry log baru masuk, maka leader akan meneruskan ke follower melalui heartbeat selanjutnya. Setelah dapat acknowledgement dari majority follower, maka entry tersebut akan dicommit oleh leader.**
5. Aktifkan Network Partition → apa yang terjadi pada minority partition?
![image](https://hackmd.io/_uploads/BJZIJr86Zl.png)
![image](https://hackmd.io/_uploads/H1Gw1BLpWl.png)
**Dalam skenario network partition, misalkan berbagai node punya term dan leader yang berbeda yang kemudian disatukan, mereka akan saling mengirimkan heartbeat. Node yang punya term lebih rendah akan stepdown dan mengikuti log dari leader lain dengan term yang lebih tinggi (term 8 dalam hal ini).**

### Pertanyaan
1. Pada saat re-election, apakah node dengan log yang lebih pendek bisa jadi leader? Mengapa?
**Dalam praktiknya tidak, karena node akan dipilih dengan log yang lebih lengkap, sehingga kalau ada node dengan log lebih pendek, maka kemungkinan tidak akan menang voting jika ada node dengan log lebih baru.**
2. Berapa minimum server yang harus aktif agar sistem tetap berfungsi (dari 5 server)?
**Minimal ada sebanyak mayoritas, 5/2 + 1, yaitu 3 server.**
3. Apa yang terjadi pada entry yang belum commit saat leader crash?
**Uncommitted log tidak dijamin bertahan, bisa saja leader baru overwrite entry tersebut, tapi bisa juga lanjutkan entrynya kalau memang cocok.**
4. Bandingkan dengan ZooKeeper: siapa yang handle write saat leader down?
**Sama saja di keduanya, tidak ada yang handle write, harus reelection dulu baru lanjut write, ada downtime kecil.**
## Lab 3 – etcd sebagai Raft-based KV Store
Tugas Modifikasi: 

1. Tambahkan watcher untuk key /config/timeout secara paralel.
![image](https://hackmd.io/_uploads/S1FBWUUTWg.png)
2. Implementasikan leader election dengan 2 node berbeda — siapa yang menang jika keduanya campaign bersamaan? 
![image](https://hackmd.io/_uploads/H1Mw-8IT-x.png)
3. Catat output dan jelaskan mengapa hasilnya deterministik atau tidak. 

![image](https://hackmd.io/_uploads/rkVse8Iabl.png)
**Output di atas menunjukkan satu node (node-2) selalu memenangkan leader election sementara node-1 selalu kalah karena sudah ada proses transaksi compare-and-swap yang berhasil lebih dulu mengisi key /election/my-service/leader. Jadi dari sisi hasil akhir, sistem terlihat deterministik: hanya satu leader yang valid pada satu waktu, dan node lain konsisten menjadi follower. Namun proses “siapa yang menang duluan” tidak sepenuhnya deterministik di level aplikasi karena dipengaruhi race condition thread scheduling, timing eksekusi, dan latency saat kedua node melakukan campaign secara bersamaan. Walaupun begitu, ketidakpastian ini tidak merusak konsistensi karena etcd di backend tetap menjamin atomicity lewat Raft consensus, sehingga hasil akhirnya selalu valid secara global meskipun urutan eksekusi di client bisa berbeda tiap run.**
## Lab 4 – Vector Clock: Implementasi & Analisis
![image](https://hackmd.io/_uploads/H1IHUSLabe.png)
1. Jalankan kode, verifikasi output a → b = True
**Pada skenario pertama, dapat dilihat bahwa a -> b bernilai true, karena dari aturannya, semua elemen dari b <= elemen dari a, dan minimal ada satu elemen b yang < elemen a. Dalam hal ini, sesuai karena memang P2 menerima dari P1 sebelum kirim.**
2. Buat skenario di mana dua event concurrent (tidak ada yang precede yang lain) — tunjukkan dengan concurrent()
**Pada skenario kedua, aturan sebelumnya tidak berlaku, karena untuk a -> c, tidak semua elemen dari b <= a, begitu pula dari c -> a, sehingga a || c bernilai true atau concurrent.**
3. Bandingkan: apakah Lamport Clock bisa mendeteksi concurrency yang sama?
**Tidak bisa, seperti percobaan sebelumnya, lamport hanya menggunakan timestamp untuk menandakan urutan, bukan hubungan konkurensi. Ketika a -> c, sudah pasti t(a) < t(c), tetapi bukan berarti ketika t(x) < t(z), selalu berarti x -> z.**
4. Tambah proses P3 yang mengirim pesan ke P1 secara bersamaan dengan P2 — gambar diagram vector clock-nya
![image](https://hackmd.io/_uploads/Hk1u5rLaWe.png)
![[skt] koordinasi-Page-2](https://hackmd.io/_uploads/SJqBjrI6Ze.jpg)
**Dalam skenario di atas, data dari P2 yang masuk terlebih dahulu, sehingga counter vector awal sebelum data P3 masuk adalah [1, 1, 0], yang kemudian akan dimerge dan menjadi [2, 1, 1] sebagai hasil akhir.**
