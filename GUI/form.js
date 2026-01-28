const form = document.getElementById("promptform");
const socket = io();

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const promptValue = document.getElementById("prompt").value;
  document.querySelector("fieldset").disabled = true;
  document.querySelector(".loading").style.visibility = "visible";

  socket.emit("query", JSON.stringify({ text: promptValue }));
});

socket.on("response", (msg) => {
  data = JSON.parse(msg);

  document.getElementById("response").innerHTML =
    "Odpověď: " + data.humanResponse + "<br>" + "Nápoj : " + data.reply;
  document.querySelector("fieldset").disabled = false;
  document.querySelector(".loading").style.visibility = "hidden";
});
