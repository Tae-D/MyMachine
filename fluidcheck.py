import requests
import json

username = "Admin"
password = "123456"
domain="http://localhost:8080"


def check():
    sync()
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        #print("could not login")
        return False
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    list=requests.get(f"{domain}/api/pump/",headers=headersrecipe)
    if list.status_code != 200:
        #print("could not get ingredient list")
        return False
    list=list.json()
    for i in list:
        pass
        #print(f"pump{i["id"]}: {i["currentIngredient"]["name"]} id:{i["currentIngredient"]["id"]} -> {i["fillingLevelInMl"]}ml")

def sync():
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        #print("could not login")
        return 0
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    list=requests.get(f"{domain}/api/pump/",headers=headersrecipe)
    if list.status_code != 200:
        #print("could not get ingredient list")
        return 0
    else:
        list=list.json()
        fluid={}
        for i in list:
            #print(i)
            fluid[i["currentIngredient"]["name"]]=i["fillingLevelInMl"]
        with open("data.json", "w") as f:
            json.dump(fluid, f, indent=4)
        return fluid

def feasibility(recipeid: int,ml):
    authurl = f"{domain}/api/auth/login"
    token = requests.post(authurl, json={"username": username, "password": password, "remember": "false"})
    if token.status_code != 200:
        #print("could not login")
        return False
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    recipe=requests.put(f"{domain}/api/cocktail/{recipeid}/feasibility", headers=headersrecipe,json={"amountOrderedInMl":ml,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]})
    if recipe.status_code != 200:
        #print(recipe.status_code)
        #print("could not check feasibility")
        return False
    if recipe.json().get("feasible", False):
        return True
    else:
        ##print("not feasible")
        #for i in recipe.json().get("requiredIngredients", []):
        #    #print(f"{i["ingredient"]["name"]} {i["ingredient"]["id"]} needs {i["amountMissing"]}ml")
        return False

def feasibility_list(ml):
    sync()
    recipes_list=[]
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    recipes = requests.get(f"{domain}/api/recipe/", headers=headersrecipe)
    if recipes.status_code == 200:
        recipes = recipes.json()
        for i in range(recipes.get("totalPages")):
            pageurl=f"{domain}/api/recipe/?page={i}&fabricable=auto"  #works only with recipes from demo. If you want to add your own recipes, delete "&inCategory=1"
            pagerecipes = requests.get(pageurl, headers=headersrecipe)
            pagerecipes=pagerecipes.json()
            #print(f"downloading recipes {i+1}/{recipes.get("totalPages")}")
            content=pagerecipes.get("content",[])
            for i in content:
                if feasibility(i["id"],ml):
                    recipes_list.append(i)
        #print(f"downloaded {len(recipes_list)} recipes")
    else:
        #print(
        #    f"Couldn't connect to recipe database, try again later. Error code: {recipes.status_code}")
        return []
    return recipes_list


def call(recipeid, ml):
    if feasibility(recipeid,ml):
        authurl = f"{domain}/api/auth/login"
        token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
        if token.status_code != 200:
            #print("could not login")
            return 1
        headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
        list = requests.put(f"{domain}/api/cocktail/{recipeid}", headers=headersrecipe, json={"amountOrderedInMl":ml,"customisations":{"boost":100,"additionalIngredients":[]},"ingredientGroupReplacements":[]})
        #print(list)
        #print(requests.post(f"{domain}/api/cocktail/continueproduction", headers=headersrecipe))
        check()
        sync()
        return 0

def fill(pumpid, ml):
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    if token.status_code != 200:
        #print("could not login")
        return 1
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    code=requests.patch(f"{domain}/api/pump/{pumpid}", headers=headersrecipe, json={"pin":None,"fillingLevelInMl":ml,"enablePin":None,"stepPin":None,"type":"dc"})
    #print(code.status_code)
    if code.status_code != 200:
        #print("could not fill")
        return 1
    else:
        #print(f"filled pump {pumpid} to {ml}")
        return 0


if __name__ == "__main__":
    match "demo":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"
    #print(domain)
    username = "Admin"
    password = "123456"
    #check()
    call(167,200)
    #feasibility(167)
    ##print(feasibility_list(10))
    #fill(5 ,500)
