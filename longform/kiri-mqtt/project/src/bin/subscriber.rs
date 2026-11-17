//! Subscribes to every sensor topic and prints each message it receives.
use rumqttc::{AsyncClient, Event, MqttOptions, Packet, QoS};
use std::time::Duration;
use tokio::signal::unix::{SignalKind, signal};

#[tokio::main]
async fn main() {
    let host = std::env::var("MQTT_HOST").unwrap_or_else(|_| "localhost".to_string());

    let mut options = MqttOptions::new("rust-subscriber", host.as_str(), 1883);
    options.set_keep_alive(Duration::from_secs(5));
    let (client, mut eventloop) = AsyncClient::new(options, 10);

    // "#" is the multi-level wildcard: sensors/room1/temperature matches.
    client
        .subscribe("sensors/#", QoS::AtLeastOnce)
        .await
        .expect("subscribe failed");
    println!("subscriber: listening on sensors/# at {host}:1883");

    // Containers are stopped with SIGTERM; Ctrl+C sends SIGINT.
    let mut term = signal(SignalKind::terminate()).expect("SIGTERM handler");
    let mut int = signal(SignalKind::interrupt()).expect("SIGINT handler");

    loop {
        tokio::select! {
            _ = term.recv() => break,
            _ = int.recv() => break,
            event = eventloop.poll() => match event {
                Ok(Event::Incoming(Packet::Publish(msg))) => {
                    let text = String::from_utf8_lossy(&msg.payload);
                    println!("received on {}: {}", msg.topic, text);
                }
                Ok(_) => {} // pings, acks and other protocol traffic
                Err(e) => {
                    eprintln!("connection error: {e}, retrying...");
                    tokio::time::sleep(Duration::from_secs(1)).await;
                }
            },
        }
    }
    client.disconnect().await.ok();
    println!("subscriber: bye");
}
