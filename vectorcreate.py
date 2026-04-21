import chromadb
from chromadb.utils import *
import requests

def recipelist(domain):
    recipes_list = []
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={"username": "Admin", "password": 123456, "remember": "false"}))
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}
    recipes = requests.get(f"{domain}/api/recipe/", headers=headersrecipe)
    if recipes.status_code == 200:
        recipes = recipes.json()
        for i in range(recipes.get("totalPages")):
            pageurl = f"{domain}/api/recipe/?page={i}&inCategory=1"  # works only with recipes from demo. If you want to add your own recipes, delete "&inCategory=1"
            pagerecipes = requests.get(pageurl, headers=headersrecipe)
            pagerecipes = pagerecipes.json()
            print(f"downloading recipes {i + 1}/{recipes.get("totalPages")}")
            content = pagerecipes.get("content", [])
            for drink in content:
                recipes_list.append({"id":drink["id"],"name":drink["name"],"description":drink["description"],"ingredients":[g["name"] for g in drink["ingredients"]]})
        print(f"downloaded {len(recipes_list)} recipes")
    else:
        print(
            f"Couldn't connect to recipe database, try again later. Error code: {recipes.status_code}")
        return []
    return recipes_list

def createvector(recipes):
    client=chromadb.PersistentClient(path="./vectorclient")
    client.delete_collection(name="vectordata")
    collection=client.create_collection(name="vectordata")
    ids=[]
    documents=[]
    metadatas=[]
    for recipe in recipes:
        ids.append(str(recipe["id"]))
        aitext=(f"Name: {recipe['name']}. "
                f"Ingredients: {recipe['ingredients']}. "
                f"Description: {recipe['description']}")
        documents.append(aitext)
        metadatas.append({"name": recipe["name"], "ingredients": recipe["ingredients"]})

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print("vectorová databáze vytvořena")
    return collection


if __name__ == "__main__":
    recipes=recipelist("https://demo.cocktailpi.org")
    recipecollection=createvector(recipes)
    testprompt="I had a hard test, recommend me something"
    result = recipecollection.query(query_texts=[testprompt],n_results=10)
    print(result)