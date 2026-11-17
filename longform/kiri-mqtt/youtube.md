# YouTube draft (NOT posted; waiting for the owner's approval)

## Title
Kiri on Linux: Install + MQTT Pub/Sub in Rust with Docker Compose (only 23 MB RAM!)

## Description
Install Kiri, the tiny Rust container engine, on Linux, then build an MQTT publisher and subscriber in Rust, test them against a Mosquitto broker, and run all three as containers with Docker Compose on Kiri. Then we check the real resource usage with htop: the Kiri engine plus all three containers use about 23 MB of RAM. Every step, every command, all the code.

🔗 All code from this video:
https://github.com/ShreyashSarage/Youtube_automation/tree/main/longform/kiri-mqtt/project

⏱️ Chapters
0:00 What we're building
0:44 What is Kiri?
1:13 What we'll build
1:37 Step 1 · Check cgroup v2
1:57 Step 2 · Download & verify
2:26 Step 3 · Install Kiri
3:09 Step 4 · First container
3:30 Step 5 · Create the Rust project
4:31 Step 6 · The publisher
5:58 Step 7 · The subscriber
7:36 Step 8 · Build & test locally
8:30 Step 9 · Containerize
10:00 Step 10 · Run it on Kiri
10:54 Step 11 · Resource usage (htop)

💻 Commands
stat -fc %T /sys/fs/cgroup                      # must print cgroup2fs
cd ~/Downloads
sha256sum -c --ignore-missing SHA256SUMS-linux  # kiri_0.2.1_amd64.deb: OK
sudo apt install ./kiri_0.2.1_amd64.deb         # Fedora: sudo dnf install ./kiri-*.rpm
sudo kiri host-access $USER
systemctl is-active kiri
docker run --rm alpine echo "hello from kiri"

cargo new mqtt-demo && cd mqtt-demo
cargo add rumqttc --no-default-features
cargo add tokio --features full
mkdir -p src/bin mosquitto && rm src/main.rs
cargo build --release

docker run -d --name test-broker -p 1883:1883 eclipse-mosquitto:2 mosquitto -c /mosquitto-no-auth.conf
cargo run --release --bin subscriber    # terminal 2
cargo run --release --bin publisher     # terminal 1
docker rm -f test-broker

docker compose up --build
docker compose ps
docker exec mqtt-demo-broker-1 mosquitto_sub -t 'sensors/#' -v -C 3
htop -F 'kiri|mosquitto|publisher|subscriber'   # press H (hide threads), F5 (tree), q (quit)
docker compose down

📦 Versions used: Kiri 0.2.1 (docker CLI 29.9.2, Compose v5.6.1), Rust 1.97, rumqttc 0.25.1, tokio 1.54.1, eclipse-mosquitto:2

📖 Links
Kiri: https://github.com/libracoder/kiri  ·  downloads: https://runkiri.com/releases/
rumqttc: https://docs.rs/rumqttc
Mosquitto: https://mosquitto.org

⚠️ allow_anonymous true is for this local demo only. Use a password file (or TLS) in production.
⚠️ Members of the kiri group can run containers as root on the machine, like the docker group.

#rust #rustlang #docker #mqtt #linux #kiri #iot #mosquitto #devops #containers #programming #tutorial

## Tags
kiri, kiri linux, htop, kiri container runtime, docker desktop alternative, rust container runtime, mqtt rust, rumqttc, mosquitto docker, mqtt publish subscribe, rust mqtt tutorial, docker compose mqtt, rust iot, tokio, linux containers, rust tutorial, mqtt tutorial

## Settings
Category: Science & Technology (28) · Language: en · Visibility: public (or scheduled) · Not made for kids
Subtitles: upload build/kiri_mqtt_tutorial.srt (Studio → Subtitles → Upload file → With timing)
