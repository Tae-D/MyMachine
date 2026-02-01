import requests
import json
import os

username = "Admin"
password = "123456"
domain="https://demo.cocktailpi.org"

def load_data(filename):
    # Check if file exists and is not empty
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("file is corrupted. Try using sync() command.")
                return {}
    else:
        print("file not found. Try using sync() command.")
        return {}

def sync():
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        print("could not login")
        exit(1)
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    list=requests.get(f"{domain}/api/ingredient/?filterIngredientGroups=true", headers=headersrecipe)
    if list.status_code != 200:
        print("could not get ingredient list")
        exit(1)
    else:
        list=list.json()
        fluid={}
        for i in list:
            fluid[i.get("id")]=i.get("bottleSize", 10)
        with open("data.json", "w") as f:
            json.dump(fluid, f, indent=4)
        print("sync successful")
        return fluid

def feasibility(recipeid):
    fs=True
    fluid_dict=load_data("data.json")
    authurl = f"{domain}/api/auth/login"
    token = requests.post(authurl, json={"username": username, "password": password, "remember": "false"})
    if token.status_code != 200:
        print("could not login")
        return False
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    recipe=requests.get(f"{domain}/api/recipe/{recipeid}?isIngredient=false", headers=headersrecipe)
    if recipe.status_code != 200:
        print("could not get recipe")
        return False
    else:
        recipe=recipe.json()
        print(recipe.get("name"))
        for i in recipe["productionSteps"][0]["stepIngredients"]:
            if str(i["ingredient"]["id"]) not in fluid_dict:
                print(f"\nunsynced ingredient {i['ingredient']['name']} id:{i['ingredient']['id']}")
                print("to sync ngredients type sync() into terminal")
                fs=False
        if not fs:
            return False
        for u in recipe["productionSteps"][0]["stepIngredients"]:
            print(f"{u['ingredient']['name']} {u["amount"]}ml/{fluid_dict[str(u["ingredient"]["id"])]}ml")
            if not fluid_dict[str(u["ingredient"]["id"])]-u["amount"]>0:
                print(f"NOT enough {u['ingredient']['name']} id:{u['ingredient']['id']}, required: {u["amount"]}ml/{fluid_dict[str(u["ingredient"]["id"])]}ml")
                fs=False
        if not fs:
            return False
        else:
            print(f"{recipe.get("name")} is feasible")
            return True

def call(recipeid):
    if feasibility(recipeid):
        authurl = f"{domain}/api/auth/login"
        token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
        if token.status_code != 200:
            print("could not login")
            exit(1)
        headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
        list = requests.put(f"{domain}/api/cocktail/{recipeid}", headers=headersrecipe, json={"amountOrderedInMl":300,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]})
        print(list)
        print(requests.post(f"{domain}/api/cocktail/continueproduction", headers=headersrecipe))
        headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
        recipe = requests.get(f"{domain}/api/recipe/{recipeid}?isIngredient=false", headers=headersrecipe)
        if recipe.status_code != 200:
            print("could not get recipe")
            return False
        else:
            fluid_dict = load_data("data.json")
            recipe=recipe.json()
            print("")
            for u in recipe["productionSteps"][0]["stepIngredients"]:
                print(f"{u['ingredient']['name']}-{fluid_dict[str(u["ingredient"]["id"])]-u["amount"]}ml")
                fluid_dict[str(u["ingredient"]["id"])] -= u["amount"]
                with open("data.json", "w") as f:
                    json.dump(fluid_dict, f, indent=4)

def refill(ingredientid, ml):
    fluid_dict = load_data("data.json")
    if str(ingredientid) in fluid_dict:
        fluid_dict[str(ingredientid)] = ml
        with open("data.json", "w") as f:
            json.dump(fluid_dict, f, indent=4)
        print(f"refilled id:{ingredientid} with {ml}ml")
    else:
        print(f"there is no ingredient with id:{ingredientid}")

if __name__ == "__main__":
    match "local":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"
    print(domain)
    username = "Admin"
    password = "123456"
    #sync()
    #call(300)
    #refill(104, 10000000000000)
    #feasibility(300)
