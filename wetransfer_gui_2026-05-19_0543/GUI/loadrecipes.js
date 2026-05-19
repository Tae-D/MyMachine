const loginUrl = "http://localhost:8080/api/auth/login";
const dataUrl = "http://localhost:8080/api/recipe/";

const loginXhr = new XMLHttpRequest();
loginXhr.open("POST", loginUrl, true);
loginXhr.setRequestHeader("Content-Type", "application/json");

loginXhr.onload = function() {
    if (loginXhr.status === 200) {

        const response = JSON.parse(loginXhr.responseText);
        const myToken = response.accessToken;
        

        sendAuthenticatedRequest(myToken);
    }
};
 
loginXhr.send(JSON.stringify({ username: "admin", password: "123456", remember: false}));


function sendAuthenticatedRequest(token) {
    const dataXhr = new XMLHttpRequest();
    dataXhr.open("GET", dataUrl, true);
    
    dataXhr.setRequestHeader("Authorization", "Bearer " + token);
    
    dataXhr.onload = function() {
        if (dataXhr.status === 200) {
            let response = JSON.parse(dataXhr.responseText);
            for(let i=0; i<response.content.length;i++){
                let drink = response.content[i]
                document.querySelector(".grid").innerHTML += `
            <div onclick="if(event.target.tagName!='BUTTON'){this.classList.toggle('expand');}" class="pokus">

                <img src="http://localhost:8080/api/recipe/${drink.id}/image" alt="obrázek k receptu ${drink.name}" class="visible">
                <div class="visible nazev">${drink.name}</div>

                <div class="invisible popis">${drink.description}</div>

                <div class="invisible ingredience">Ingredience: ${drink.ingredients.map(x=>x.name)}</div>

                <button class="pripravit invisible" onclick="makeCoctail(${drink.id})">▶</button>
            </div>`
            }
        }
    };
    
    dataXhr.send();
}











function makeCoctail(id) {
    const loginUrl = "http://localhost:8080/api/auth/login";
    const baseUrl = `http://localhost:8080/api/cocktail/${id}`;

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





let timeout;

function resetTimer() {
    clearTimeout(timeout);
    
    timeout = setTimeout(() => {
        history.back()
    }, 15000); 
}


window.onload = resetTimer;
window.onmousemove = resetTimer;
window.onmousedown = resetTimer;
window.ontouchstart = resetTimer;
window.onclick = resetTimer;     
window.onkeydown = resetTimer;
