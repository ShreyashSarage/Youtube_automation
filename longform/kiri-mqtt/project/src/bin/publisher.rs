//! Publishes a fake temperature reading to the MQTT broker every 2 seconds.
use rumqttc::{AsyncClient, MqttOptions, QoS};
use std::time::Duration;
use tokio::time;

#[tokio::main]
async fn main() {
    // Broker address comes from the environment, so the same binary works
    // on your laptop (localhost) and inside a container (the service name).
    let host = std::env::var("MQTT_HOST").unwrap_or_else(|_| "localhost".to_string());
    let topic = "sensors/room1/temperature";

    let mut options = MqttOptions::new("rust-publisher", host.as_str(), 1883);
    options.set_keep_alive(Duration::from_secs(5));
    let (client, mut eventloop) = AsyncClient::new(options, 10);

    // The event loop does the actual network I/O, so it runs in its own task.
    tokio::spawn(async move {
        loop {
            if let Err(e) = eventloop.poll().await {
                eprintln!("connection error: {e}, retrying...");
                time::sleep(Duration::from_secs(1)).await;
            }
        }
    });

    println!("publisher: sending to {topic} on {host}:1883");
    for i in 1..=10 {
        let temp = 22.0 + (i % 5) as f32 * 0.5;
        let payload = format!(r#"{{"reading":{i},"celsius":{temp:.1}}}"#);
        client
            .publish(topic, QoS::AtLeastOnce, false, payload.clone())
            .await
            .expect("publish failed");
        println!("published #{i}: {payload}");
        time::sleep(Duration::from_secs(2)).await;
    }
    println!("publisher: done");
}
