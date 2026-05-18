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
  console.log(msg)
  let data = msg

  document.getElementById("response").innerHTML =
    "Odpověď: " + data.humanResponse + "<br>" + "Nápoj : " + data.name;
  document.querySelector("fieldset").disabled = false;
  document.querySelector(".loading").style.visibility = "hidden";
  document.querySelector("#prompt").value = "";
  document.querySelector("#pripravit").dataset.id = data.id;
  document.querySelector("#pripravit").onclick = (event) => {makeCoctail(event.target.dataset.id)};
});



let timeout;

function resetTimer() {
    clearTimeout(timeout);
    
    timeout = setTimeout(() => {
      if(document.querySelector("#response").innerHTML == "" && document.querySelector(".loading").style.visibility == "hidden"){
        history.back()
      }
    }, 15000); 
}


window.onload = resetTimer;
window.onmousemove = resetTimer;
window.onmousedown = resetTimer;
window.ontouchstart = resetTimer;
window.onclick = resetTimer;     
window.onkeydown = resetTimer;



function makeCoctail(id) {
    const loginUrl = "http://localhost/api/auth/login";
    const baseUrl = `http://localhost/api/cocktail/${id}`;

    const loginXhr = new XMLHttpRequest();
    loginXhr.open("POST", loginUrl, true);
    loginXhr.setRequestHeader("Content-Type", "application/json");

    loginXhr.onload = function() {
        if (loginXhr.status === 200) {
            const response = JSON.parse(loginXhr.responseText);
            const myToken = response.accessToken;
            
            // 1. Krok: Ověření proveditelnosti (feasibility)
            checkFeasibility(myToken, id);
        }
    };
    
    loginXhr.send(JSON.stringify({ username: "admin", password: "123456", remember: false }));

    function checkFeasibility(token, drinkId) {
        const featXhr = new XMLHttpRequest();
        featXhr.open("PUT", `${baseUrl}/feasibility`, true);
        featXhr.setRequestHeader("Content-Type", "application/json");
        featXhr.setRequestHeader("Authorization", "Bearer " + token);

        featXhr.onload = function() {
            if (featXhr.status === 200) {
                const result = JSON.parse(featXhr.responseText);
                
                if (result === true || result.feasible === true) {
                    console.log("Koktejl lze vyrobit, odesílám požadavek...");
                    executeMake(token);
                } else {
                    alert("Chybí ingredience pro tento koktejl.");
                }
            }
        };
        featXhr.send(`{"amountOrderedInMl":150,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]}`);
    }

    function executeMake(token) {
        const makeXhr = new XMLHttpRequest();
        makeXhr.open("PUT", baseUrl, true);
        makeXhr.setRequestHeader("Content-Type", "application/json");
        makeXhr.setRequestHeader("Authorization", "Bearer " + token);

        makeXhr.onload = function() {
            if (makeXhr.status === 202) {
                alert("Koktejl se připravuje!");
            } else {
                alert("Chyba při výrobě koktejlu.");
            }
        };
        makeXhr.send(`{"amountOrderedInMl":150,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]}`);
    }
}