const form = document.getElementById("promptform");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const promptValue = document.getElementById("prompt").value;
  document.querySelector("fieldset").disabled = true;
  document.querySelector(".loading").style.visibility = "visible";
  try {
    // "http://localhost:5000/process" je adresa vašeho Python serveru
    const response = await fetch("http://localhost:5000/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: promptValue }),
    });
    const data = await response.json();
    document.getElementById("response").innerHTML =
      "Odpověď: " + data.humanResponse + "<br>" + "Nápoj : " + data.reply;
    document.querySelector("fieldset").disabled = false;
    document.querySelector(".loading").style.visibility = "hidden";
  } catch (error) {
    console.error("Chyba:", error);
  }
});
