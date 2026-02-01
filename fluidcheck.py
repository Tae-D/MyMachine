import requests
import json

username = "Admin"
password = "123456"
domain="https://demo.cocktailpi.org"


def check():
    sync()
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        print("could not login")
        return False
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    list=requests.get(f"{domain}/api/pump/",headers=headersrecipe)
    if list.status_code != 200:
        print("could not get ingredient list")
        return False
    list=list.json()
    for i in list:
        print(f"pump{i["id"]}: {i["currentIngredient"]["name"]} id:{i["currentIngredient"]["id"]} -> {i["fillingLevelInMl"]}ml")

def sync():
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        print("could not login")
        exit(1)
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    list=requests.get(f"{domain}/api/pump/",headers=headersrecipe)
    if list.status_code != 200:
        print("could not get ingredient list")
        exit(1)
    else:
        list=list.json()
        fluid={}
        for i in list:
            fluid[i["currentIngredient"]["id"]]=i["fillingLevelInMl"]
        with open("data.json", "w") as f:
            json.dump(fluid, f, indent=4)
        return fluid

def feasibility(recipeid,ml):
    authurl = f"{domain}/api/auth/login"
    token = requests.post(authurl, json={"username": username, "password": password, "remember": "false"})
    if token.status_code != 200:
        print("could not login")
        return False
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    recipe=requests.put(f"{domain}/api/cocktail/{recipeid}/feasibility", headers=headersrecipe,json={"amountOrderedInMl":ml,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]})
    if recipe.status_code != 200:
        print("could not check feasibility")
        return False
    if recipe.json().get("feasible", False)==True:
        print("feasible")
        return True
    else:
        print("not feasible")
        for i in recipe.json().get("requiredIngredients", []):
            print(f"{i["ingredient"]["name"]} {i["ingredient"]["id"]} needs {i["amountMissing"]}ml more out of {i["amountRequired"]}ml")
        return False


def call(recipeid, ml):
    if feasibility(recipeid,ml):
        authurl = f"{domain}/api/auth/login"
        token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
        if token.status_code != 200:
            print("could not login")
            exit(1)
        headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
        list = requests.put(f"{domain}/api/cocktail/{recipeid}", headers=headersrecipe, json={"amountOrderedInMl":ml,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]})
        print(list)
        print(requests.post(f"{domain}/api/cocktail/continueproduction", headers=headersrecipe))
        check()
        sync()


if __name__ == "__main__":
    match "local":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"
    print(domain)
    username = "Admin"
    password = "123456"
    #check()
    #sync()
    call(167,50)
    #feasibility(167)
