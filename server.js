const fs = require("fs");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const path = require("path");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}


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
  socket.on("query", (msg) => {
    console.log("Message received:", msg);
    io.emit("response", '{"reply": "Rockshandy", "suggestedRecipeId": 251, "reasoningSummary": "User needs something against thirst.", "humanResponse": "Tady je tvoje Rockshandy, obsahuje citrónovou sodu, která je výborná proti žízni"}');
  });

  // Handle disconnection
  socket.on("disconnect", () => {
    console.log("A user disconnected");
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
