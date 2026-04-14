const fs = require("fs");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const path = require("path");
const nodecallspython = require("node-calls-python")

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const py = nodecallspython.interpreter;

// Serve static files
app.use(express.static(path.join(__dirname, "GUI")));

// Simple route
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Socket.IO connection handler
io.on("connection", (socket) => {
  console.log("A user connected");

  // Handle new messages
  socket.on("query", async (msg) => {
    console.log("Message received:", msg);
    let module = await py.import("./AIrecipeTEST.py");
    let result = await py.call(module, "main");
    io.emit("response", result);
  });

  // Handle disconnection
  socket.on("disconnect", () => {
    console.log("A user disconnected");
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, "127.0.0.1", () => {
  console.log(`Server running on port ${PORT}`);
});




a = {
            "id": 1,
            "name": "20th Century",
            "ownerName": "Admin",
            "description": "Evoking the glamour of classic rail travel, the 20th Century cocktail delivers a bright and sophisticated flavor journey. Zesty lemon meets aromatic gin, while coffee liqueur adds a deep richness, all balanced by the crisp, herbal elegance of Lillet Blanc. Enjoy this cocktail when you crave a timeless, refreshing experience with a hint of intrigue.",
            "hasImage": true,
            "ingredients": [
                {
                    "id": 38,
                    "name": "Coffee Liqueur",
                    "alcoholContent": 25,
                    "inBar": false,
                    "onPump": false,
                    "type": "automated"
                },
                {
                    "id": 80,
                    "name": "Lemon Juice",
                    "alcoholContent": 0,
                    "inBar": false,
                    "onPump": false,
                    "type": "automated"
                },
                {
                    "id": 62,
                    "name": "Gin",
                    "inBar": false,
                    "onPump": false,
                    "type": "group"
                },
                {
                    "id": 87,
                    "name": "Lillet Blanc",
                    "alcoholContent": 17,
                    "inBar": false,
                    "onPump": false,
                    "type": "automated"
                }
            ],
            "lastUpdate": "2026-01-05T16:32:12.000+00:00",
            "minAlcoholContent": 28,
            "maxAlcoholContent": 28,
            "type": "recipe"
        }