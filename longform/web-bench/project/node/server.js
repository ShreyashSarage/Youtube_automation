// Node.js: Express 5, one worker per CPU core (node:cluster)
const cluster = require("node:cluster");
const os = require("node:os");
const express = require("express");

if (cluster.isPrimary) {
  for (let i = 0; i < os.availableParallelism(); i++) cluster.fork();
} else {
  const app = express();
  app.use(express.json());

  app.get("/api/user/:id", (req, res) => {
    const id = Number(req.params.id);
    res.json({ id, name: `user${id}`, email: `user${id}@example.com`, roles: ["reader", "writer"] });
  });

  app.post("/api/orders", (req, res) => {
    const items = req.body.items;
    const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
    res.json({ items: items.length, total });
  });

  app.listen(8080, "127.0.0.1");
}
