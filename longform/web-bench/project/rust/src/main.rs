// Rust: axum on tokio
use axum::{Json, Router, extract::Path, routing::{get, post}};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct User { id: u64, name: String, email: String, roles: Vec<&'static str> }

#[derive(Deserialize)]
struct Item { price: f64, qty: u32 }

#[derive(Deserialize)]
struct Order { items: Vec<Item> }

#[derive(Serialize)]
struct Total { items: usize, total: f64 }

async fn user(Path(id): Path<u64>) -> Json<User> {
    Json(User {
        id,
        name: format!("user{id}"),
        email: format!("user{id}@example.com"),
        roles: vec!["reader", "writer"],
    })
}

async fn order(Json(o): Json<Order>) -> Json<Total> {
    let total = o.items.iter().map(|i| i.price * i.qty as f64).sum();
    Json(Total { items: o.items.len(), total })
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/user/{id}", get(user))
        .route("/api/orders", post(order));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
