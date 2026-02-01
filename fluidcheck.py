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
                print(f"\nunsynced ingredient {i['ingredient']['name']}")
                print("to sync ngredients type sync() into terminal")
                fs=False
        if not fs:
            return False
        for u in recipe["productionSteps"][0]["stepIngredients"]:
            print(f"{u['ingredient']['name']} {u["amount"]}ml/{fluid_dict[str(u["ingredient"]["id"])]}ml")
            if not fluid_dict[str(u["ingredient"]["id"])]-u["amount"]>0:
                print(f"\nnot enogh {u['ingredient']['name']}")
                print(f"required: {u["amount"]}ml/{fluid_dict[str(u["ingredient"]["id"])]}ml")
                fs=False
        if not fs:
            return False
        else:
            print(f"{recipe.get("name")} is feasible")
            return True



if __name__ == "__main__":
    match "local":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"
    print(domain)
    username = "Admin"
    password = "123456"
    sync()
    feasibility(10)
