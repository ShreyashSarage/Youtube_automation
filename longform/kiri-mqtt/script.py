"""Shot list for "Kiri on Linux + MQTT pub/sub in Rust" (horizontal screencast).

Every command output comes from a real run on Kiri (captures/*.json) or, for the
steps that can only happen on a normal Ubuntu machine (download, apt install,
host-access), from Kiri's own packaging/source messages (see NOTES at the end).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "project")
CAP1 = {c["cmd"]: c for c in json.load(open(os.path.join(HERE, "captures/cap1.json")))}
CAP2 = json.load(open(os.path.join(HERE, "captures/cap2.json")))
def cap2(cmd): return next(c for c in CAP2 if c["cmd"] == cmd)
def src(path): return open(os.path.join(PROJ, path)).read().rstrip("\n").split("\n")

PROMPT_DIR = {"home": "~", "dl": "~/Downloads", "proj": "~/mqtt-demo"}

def clean_cargo_add(out):
    return out.rstrip("\n")

def compose_up_lines():
    """Real `docker compose up --build` output on Kiri, minus the two sandbox-only
    build steps (proxy CA for cargo); build steps renumbered to the tutorial Dockerfile."""
    lines = cap2("docker compose up --build")["timed"]; out = []; skip = False
    for t, l in lines:
        m = re.match(r"#(\d+) ", l)
        if "sandbox" in l or "update-ca-certificates" in l: skip = True; continue
        if skip and (m or l == ""):
            if l == "": skip = False
            continue
        skip = False
        l = re.sub(r"\[(publisher|subscriber) build (\d)/7\]", lambda m: f"[{m.group(1)} build {max(1, int(m.group(2)) - 2) if int(m.group(2)) >= 4 else 1}/5]", l)
        if re.search(r"#\d+ (sha256|resolve|extracting)", l): continue
        if l.startswith("^C") or "Gracefully" in l: pass
        out.append((t, l))
    return out

def compose_parts():
    L = compose_up_lines()
    a = next(i for i, (t, l) in enumerate(L) if "auto-" in l and "New client" in l)
    b = next(i for i, (t, l) in enumerate(L) if "publisher-1 exited" in l)
    return L[:a], L[a:b + 1], [l for t, l in L[b + 1:] if l.strip()]

APT_OUT = """Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Note, selecting 'kiri' instead of './kiri_0.2.1_amd64.deb'
The following NEW packages will be installed:
  kiri
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Selecting previously unselected package kiri.
Preparing to unpack .../kiri_0.2.1_amd64.deb ...
Unpacking kiri (0.2.1) ...
Setting up kiri (0.2.1) ...
Kiri is installed with its own docker CLI (docker, docker compose, docker buildx).
The engine starts when you set Kiri up: open Kiri, or run  sudo kiri host-access $USER
Members of the kiri group can run containers as root on this machine; treat it like the docker group.
While no Docker engine has /var/run/docker.sock, it leads to Kiri too (for Testcontainers, docker-py and other tools that ignore docker contexts)."""

def tree_out():
    return """.
├── Cargo.lock
├── Cargo.toml
├── compose.yaml
├── Dockerfile
├── mosquitto
│   └── mosquitto.conf
└── src
    └── bin
        ├── publisher.rs
        └── subscriber.rs

4 directories, 7 files"""

def docker_ps_out():
    o = cap2("docker ps")["out"].split("\n")
    return "\n".join(l for l in o if "buildkit" not in l).rstrip()

PUB = src("src/bin/publisher.rs"); SUB = src("src/bin/subscriber.rs")
FILES = {
    "Cargo.toml": src("Cargo.toml"), "src/bin/publisher.rs": PUB, "src/bin/subscriber.rs": SUB,
    "mosquitto/mosquitto.conf": src("mosquitto/mosquitto.conf"), "Dockerfile": src("Dockerfile"),
    "compose.yaml": src("compose.yaml"),
}

def T(cmd, out="", term=1, d="proj", speed=None, pause=0.6, keys=None, stream=None):
    return dict(kind="cmd", cmd=cmd, out=out, term=term, dir=d, speed=speed, pause=pause, keys=keys, stream=stream)

# ------------------------------------------------------------------ shots
SHOTS = [
 dict(id="cold_open", scene="terminal", zoom=1.18, actions=[
   T("docker compose up", stream=[(t, l) for t, l in compose_up_lines() if "|" in l and "auto-" not in l][:26], d="proj", speed=2.5, term=3)],
   say="This is what we're building today. A Rust publisher sending sensor data to a Mosquitto MQTT broker, and a Rust subscriber receiving every message. All three are running as containers, not on Docker, but on Kiri, a tiny container engine written in Rust."),
 dict(id="intro", scene="title", title="Kiri on Linux", subtitle="Install it, then run MQTT publish/subscribe in Rust", chapter=None,
   say="Hey everyone, welcome back! In this one we'll install Kiri on Linux step by step, check that it works, then write the publisher and subscriber in Rust, test them, put everything in containers with Docker Compose, and run it on Kiri. All the code and commands are in the description, so feel free to follow along."),
 dict(id="what_is_kiri", scene="diagram", diagram="kiri", chapter="What is Kiri?",
   say="So what is Kiri? It's an open source replacement for Docker Desktop, written in Rust and licensed Apache 2.0. It speaks the Docker Engine API, so the docker command, Compose and buildx all just work. On Mac and Windows it runs a small Linux VM, but on Linux there's no VM at all. The Kiri engine runs your containers directly on your own kernel. At the time I'm recording, the latest release is 0.2.1."),
 dict(id="plan", scene="diagram", diagram="plan", chapter="What we'll build",
   say="Here's the plan. We'll have three containers. Mosquitto is the MQTT broker, basically a post office for messages. Our Rust publisher sends a temperature reading every two seconds to the topic sensors slash room1 slash temperature. And our Rust subscriber subscribes to sensors slash hash. The hash is a wildcard, so it gets everything under sensors."),
 dict(id="cgroup", scene="terminal", chapter="Step 1 · Check cgroup v2", actions=[
   T("stat -fc %T /sys/fs/cgroup", "cgroup2fs", d="home")],
   say="Okay, let's start. Kiri needs cgroup version 2, which is the default on Ubuntu 22.04 and newer, and on recent Fedora. To check, run stat dash f c percent capital T on slash sys slash fs slash cgroup. If it prints cgroup2fs, you're good to go."),
 dict(id="download", scene="terminal", chapter="Step 2 · Download & verify", actions=[
   T("cd ~/Downloads", d="home", pause=0.3),
   T("ls", "SHA256SUMS-linux  kiri_0.2.1_amd64.deb", d="dl"),
   T("sha256sum -c --ignore-missing SHA256SUMS-linux", "kiri_0.2.1_amd64.deb: OK", d="dl")],
   say="Next, go to runkiri dot com slash releases and download the dot deb for your machine. That's amd64 for most PCs, or arm64. Fedora users, grab the dot rpm instead. Also download the SHA256SUMS dash linux file next to it, so we can make sure the download isn't corrupted. Run sha256sum dash c with ignore missing, and you want to see OK."),
 dict(id="install", scene="terminal", chapter="Step 3 · Install Kiri", actions=[
   T("sudo apt install ./kiri_0.2.1_amd64.deb", APT_OUT, d="dl", speed=14, keys="[sudo] password for dev:")],
   say="Now install it with sudo apt install, and make sure you put dot slash in front of the file name, so apt knows it's a local file. Look at the messages at the end. Kiri comes with its own docker CLI, plus compose and buildx. And notice: the engine does not start yet. It starts when you set Kiri up."),
 dict(id="host_access", scene="terminal", actions=[
   T("sudo kiri host-access $USER", "dev is in the kiri group\ndev can use Kiri now", d="dl"),
   T("systemctl is-active kiri", "active", d="dl")],
   say="So let's set it up. Run sudo kiri host-access, dollar USER. This adds you to the kiri group, and enables and starts the kiri system service. Quick heads up though: being in the kiri group is basically root on this machine, same as the docker group, so only add users you trust. And systemctl is-active kiri says active. Nice."),
 dict(id="first_container", scene="terminal", chapter="Step 4 · First container", actions=[
   T("clear", d="dl", pause=0.2),
   T("docker version --format 'Client: {{.Client.Version}}  Server: {{.Server.Platform.Name}} (API {{.Server.APIVersion}})'",
     CAP1["docker version --format 'Client: {{.Client.Version}}  Server: {{.Server.Platform.Name}} (API {{.Server.APIVersion}})'"]["out"].strip(), d="dl"),
   T('docker run --rm alpine echo "hello from kiri"', CAP1['docker run --rm alpine echo "hello from kiri"']["out"].strip(), d="dl", speed=8)],
   say="Let's make sure docker is really talking to Kiri. docker version, and the server says Kiri. Now our first container: docker run, dash dash rm, alpine, echo hello from kiri. It pulls the alpine image, runs it, and prints our message. That's a real container, running straight on the Linux kernel through Kiri."),
 dict(id="new_project", scene="terminal", chapter="Step 5 · Create the Rust project", actions=[
   T("cd ~", d="dl", pause=0.2),
   T("cargo new mqtt-demo", CAP1["cargo new mqtt-demo"]["out"].strip(), d="home"),
   T("cd mqtt-demo", d="home", pause=0.2),
   T("cargo add rumqttc --no-default-features", clean_cargo_add(CAP1["cargo add rumqttc --no-default-features"]["out"]), speed=20),
   T("cargo add tokio --features full", clean_cargo_add(CAP1["cargo add tokio --features full"]["out"]), speed=20)],
   say="Now the Rust part. If you don't have Rust yet, install it with rustup, I covered that in my Rust Day 2 short. Run cargo new mqtt dash demo and go into the folder. We need two crates. rumqttc is the MQTT client. I'm adding it with no default features, because the defaults pull in TLS, and we don't need TLS for plain MQTT on port 1883, so the build stays pure Rust and much faster. And tokio with the full feature set, our async runtime."),
 dict(id="cargo_toml", scene="editor", file="Cargo.toml", show=True, highlight=[7, 8],
   say="Here's the Cargo dot toml after those two commands. rumqttc with default features turned off, and tokio with full."),
 dict(id="layout", scene="terminal", actions=[
   T("mkdir -p src/bin mosquitto && rm src/main.rs", "", pause=0.4)],
   say="One project, two programs. Anything you put in src slash bin becomes its own binary. So I'm creating src slash bin, a mosquitto folder for the broker config, and removing the default main dot rs, since we won't use it."),
 dict(id="pub1", scene="editor", file="src/bin/publisher.rs", type=(0, 12), chapter="Step 6 · The publisher",
   say="Let's write the publisher. I'm creating publisher dot r s in src slash bin. First the imports: AsyncClient, MqttOptions and QoS from rumqttc, Duration, and tokio's time. hash tokio main turns our main into an async function. The broker's host name comes from an environment variable, MQTT underscore HOST, defaulting to localhost. That way the same binary works on your machine and inside a container."),
 dict(id="pub2", scene="editor", file="src/bin/publisher.rs", type=(12, 26),
   say="Next, the connection options: a client ID, the host, and port 1883, plus a five second keep alive. AsyncClient new gives us two things: a client to send messages with, and an event loop. The event loop is what actually talks to the network, so we spawn it in its own task and keep polling it. If the connection drops, we print the error and retry after a second."),
 dict(id="pub3", scene="editor", file="src/bin/publisher.rs", type=(26, 39),
   say="And the main loop. Ten readings. For each one we make a fake temperature, format it as a small JSON string, and publish it to our topic with QoS at least once, meaning the broker has to acknowledge it. Then we print what we sent and wait two seconds."),
 dict(id="sub1", scene="editor", file="src/bin/subscriber.rs", type=(0, 20), chapter="Step 7 · The subscriber",
   say="Now the subscriber, in subscriber dot r s. Same setup: read the host, build the options with a different client ID, rust dash subscriber, because every client connected to the broker needs a unique ID. Then we subscribe to sensors slash hash, again with QoS at least once."),
 dict(id="sub2", scene="editor", file="src/bin/subscriber.rs", type=(20, 29),
   say="Here's a detail people often miss. When Docker or Kiri stops a container, it sends SIGTERM, and Ctrl plus C sends SIGINT. If your program ignores those, the container gets killed after ten seconds. So we listen for both signals, and use tokio select to wait for whichever happens first: a signal, or the next MQTT event."),
 dict(id="sub3", scene="editor", file="src/bin/subscriber.rs", type=(29, 44),
   say="When the event is an incoming publish packet, we turn the payload bytes into text and print the topic and the message. Everything else, pings and acknowledgements, we just ignore. When a signal comes in, we break out of the loop, disconnect cleanly, and say bye."),
 dict(id="build", scene="terminal", chapter="Step 8 · Build & test locally", actions=[
   T("clear", pause=0.2),
   T("cargo build --release", CAP1["cargo build --release"]["out"].strip(), speed=10)],
   say="Let's build it. cargo build dash dash release. The first build downloads and compiles the dependencies, so it takes a little while. Mine took about fifteen seconds."),
 dict(id="local_test", scene="split", actions=[
   T("docker run -d --name test-broker -p 1883:1883 eclipse-mosquitto:2 mosquitto -c /mosquitto-no-auth.conf",
     cap2("docker run -d --name test-broker -p 1883:1883 eclipse-mosquitto:2 mosquitto -c /mosquitto-no-auth.conf")["out"].strip().split("\n")[-1], speed=6),
   T("docker ps", docker_ps_out()),
   T("cargo run --release --bin subscriber", "\n".join(cap2("cargo run --release --bin subscriber")["out"].split("\n")[:1]), term=2, pause=0.8),
   T("cargo run --release --bin publisher", cap2("cargo run --release --bin publisher")["out"].strip(), speed=1.4),
   dict(kind="reveal", term=2, text="\n".join(cap2("cargo run --release --bin subscriber")["out"].strip().split("\n")[1:-1]), speed=0, sync_with_prev=True),
   dict(kind="keys", term=2, keys="Ctrl+C", text="^C\nsubscriber: bye")],
   say="Before containerizing anything, let's test it locally. I'm starting a throwaway Mosquitto broker on Kiri, publishing port 1883. The image ships a no auth config, which is handy for quick tests. Then in a second terminal I start the subscriber, and in the first one, the publisher. And look at that. Every message the publisher sends shows up in the subscriber. Ctrl plus C, and the subscriber says bye. That's our signal handling working."),
 dict(id="rm_test", scene="terminal", actions=[
   T("docker rm -f test-broker", "test-broker")],
   say="Let's clean up that test broker with docker rm dash f."),
 dict(id="mosq_conf", scene="editor", file="mosquitto/mosquitto.conf", type=(0, 99), chapter="Step 9 · Containerize",
   say="Time to containerize. First, the broker config. Mosquitto version 2 only listens on localhost by default, so other containers couldn't reach it. listener 1883 makes it listen on all interfaces, and allow anonymous true lets clients connect without a password. That's fine for a demo, but in production, use a password file."),
 dict(id="dockerfile", scene="editor", file="Dockerfile", type=(0, 99),
   say="Next, the Dockerfile. It's a multi stage build. The first stage uses the official rust image to compile both binaries in release mode. The second stage starts from debian slim and just copies the two binaries in, so the final image is small and doesn't carry the whole Rust toolchain. I also added a dot dockerignore with target in it, so the build context stays small."),
 dict(id="compose", scene="editor", file="compose.yaml", type=(0, 99),
   say="And compose dot yaml ties it together. The broker service runs eclipse mosquitto 2, publishes port 1883, and mounts our config. The subscriber and the publisher both build from our Dockerfile, run their own binary, and get MQTT underscore HOST set to broker. Inside the compose network, the service name is the host name. depends on just controls start order, and that's why the publisher retries until the broker is ready."),
 dict(id="compose_up", scene="terminal", chapter="Step 10 · Run it on Kiri", zoom=1.12, actions=[
   T("clear", pause=0.2),
   T("docker compose up --build", stream=compose_parts()[0], speed=1.0, keys=None)],
   say="Moment of truth. docker compose up dash dash build. Kiri builds both images with BuildKit, compiling our Rust code inside the container. I've sped this part up a little. And then all three containers start. The broker logs each client connecting, the publisher sends its readings, and the subscriber receives every single one. Publisher to broker to subscriber, all running on Kiri."),
 dict(id="inspect", scene="split", actions=[
   T("docker compose ps", cap2("docker compose ps")["out"].strip(), term=2),
   dict(T("docker exec mqtt-demo-broker-1 mosquitto_sub -t 'sensors/#' -v -C 3", cap2("docker exec mqtt-demo-broker-1 mosquitto_sub -t 'sensors/#' -v -C 3")["out"].strip(), term=2),
        bg=dict(term=1, lines=compose_parts()[1], sync=["published #4", "published #5", "published #6"]))],
   say="While that's running, let's peek inside from a second terminal. docker compose ps shows our three services up. And we can even use the mosquitto sub tool that comes inside the broker image, through docker exec, to listen in. Dash C three means stop after three messages. And there they are, straight from the broker."),
 dict(id="down", scene="terminal", actions=[
   dict(kind="keys", term=1, keys="Ctrl+C", text="^C\n" + "\n".join(compose_parts()[2])),
   T("docker compose down", cap2("docker compose down")["out"].strip(), speed=12)],
   say="When you're done, Ctrl plus C to stop, and docker compose down removes the containers and the network."),
 dict(id="outro", scene="title", title="That's it!", subtitle="Kiri  ·  Mosquitto  ·  Rust publisher & subscriber", outro=True,
   say="And that's it! We installed Kiri on Linux, ran our first container, wrote an MQTT publisher and subscriber in Rust, tested them locally, and ran the whole thing with Docker Compose on Kiri. All the code is in the description. If this helped, a like and a subscribe really helps the channel, and tell me in the comments what you want me to build next. See you in the next one!"),
]

NOTES = """Outputs not captured on a real Ubuntu install (they can't run in a sandbox without systemd/apt
for the official .deb): `stat` (cgroup2fs is what cgroup v2 prints), `ls`/`sha256sum` (file names
from packaging/linux/build.sh and RELEASES.md), apt's standard lines + Kiri's postinst messages
(packaging/linux/deb/postinst), host-access messages (crates/kiri/src/hostaccess.rs). Everything else
is the real output of the same commands run on Kiri (built from source) in this environment."""
