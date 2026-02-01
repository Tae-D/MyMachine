import requests
import time
import json
import os
from dotenv import load_dotenv
import argostranslate.package
import argostranslate.translate

load_dotenv()
FROM_CODE = "cs"
TO_CODE = "en"

BASEURL = "https://aihorde.net/api/v2"
API_KEY = api_key = os.getenv('API_KEY')


def install_model(source, target):
    """Checks and installs a specific language pair model."""
    try:
        # Check if already installed
        installed = argostranslate.package.get_installed_packages()
        if any(pkg.from_code == source and pkg.to_code == target for pkg in installed):
            print(f"Model {source} -> {target} is already installed.")
            return

        # Update index and find package
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()

        package = next((p for p in available if p.from_code == source and p.to_code == target), None)

        if package:
            print(f"Downloading {source} -> {target} model...")
            argostranslate.package.install_from_path(package.download())
            print("Done.")
        else:
            print(f"Model {source} -> {target} not found.")

    except Exception as e:
        print(f"Error installing {source}-{target}: {e}")


def init_translation():
    """Initializes both translation directions."""
    # Install Czech -> English
    install_model(FROM_CODE, TO_CODE)
    # Install English -> Czech
    install_model(TO_CODE, FROM_CODE)

def translate_cs_to_en(text):
    translatedText = argostranslate.translate.translate(text, FROM_CODE, TO_CODE)
    return translatedText

def translate_en_to_cs(text):
    translatedText = argostranslate.translate.translate(text, TO_CODE,FROM_CODE)
    return translatedText


def get_job_id(prompt: str):
    urlai = f"{BASEURL}/generate/text/async"
    payload = {"n": 1, "params": {"max_length": 150}, "prompt": prompt}
    headers = {}
    if API_KEY:
        headers["apikey"] = API_KEY
    response = requests.post(urlai, json=payload, headers=headers)

    if response.status_code != 200 and response.status_code != 202:
        print(
            f"error code: {response.status_code}, error message: {response.text}")
        exit(response.status_code)
    job_id = response.json().get("id")
    return job_id


def get_answer(job):
    status_url = f"{BASEURL}/generate/text/status/{job}"
    attempt = 0
    while True:
        r = requests.get(status_url)
        if r.status_code != 200 and r.status_code != 202:
            print(f"error code: {r.status_code}, error message: {r.text}")

        if r.json().get("finished"):
            absoluteresponse = r.json()["generations"][0]["text"]
            return absoluteresponse
        time.sleep(2)
        attempt += 1
        print(r.json().get("wait_time"))
        if attempt > 30 or r.json().get("wait_time") > 40:

            return False


def main(prompt: str, urlrecipe: str, username: str, password: str):
    start_time = time.time()
    authurl = f"{urlrecipe}/api/auth/login"
    token = (requests.post(authurl, json={"username": username, "password": password, "remember": "false"}))
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}

    recipes_list=[]
    recipes_sorted=[]
    attempt_generate = 0
    recipes = requests.get(f"{urlrecipe}/api/recipe/", headers=headersrecipe)
    if recipes.status_code == 200:
        recipes = recipes.json()
        for i in range(recipes.get("totalPages")): #super messy, but I cant find better way to get all recipes at once.
            pageurl=f"{urlrecipe}/api/recipe/?page={i}"  #works only with recipes from demo. If you want to add your own recipes, delete "&inCategory=1"
            pagerecipes = requests.get(pageurl, headers=headersrecipe)
            pagerecipes=pagerecipes.json()
            print(f"stahování receptů {i+1}/{recipes.get("totalPages")}")
            recipes_list.extend([[item["name"],item["id"]] for item in pagerecipes.get("content")])
            content=pagerecipes.get("content",[])
            for drink in content:
                recipes_sorted.append({"name":drink["name"],"description":drink["description"],"ingredients":drink["ingredients"]})
        print(f"stáhnuto {len(recipes_list)} receptů")
    else:
        print(
            f"Couldn't connect to recipe database, try again later. Error code: {recipes.status_code}")
        exit(2)
    prompt=translate_cs_to_en(prompt)
    print(f"\n{prompt}\n")
    while True:
        if attempt_generate > 10:  # if prompt is not that hard, it is usually enough.
            print("too many attempts, try different prompt")
            end_time = time.time()
            print(f"Time taken: {round(end_time - start_time)}s")
            exit()

        system_instruction = (
            f"You are a drink machine API. Respond ONLY in valid dictionary. Take one drink from {recipes_sorted}. "
            "The dictionary must contain four keys: 'reply', 'reasoningSummary', 'humanResponse'."
            "humanResponse should be a comment for drink, that is chosen"

        )
        example = (
            "Example Input: 'I am thirsty'\n"
            "Example Output: {\"reply\": \"Rockshandy\", \"reasoningSummary\": \"User needs something against thirst. I will give them Rockshady because it contains Lemon-Lime Soda, which is great again thirst and it is refreshing\", \"humanResponse\": \"Here is your Rockshandy, it contains lemon soda, that will be great against your thirst\"}"
        )

        finalprompt = f"{system_instruction}\n\n{example}\n\nInput: {prompt}\nOutput:"
        job_id = get_job_id(finalprompt)
        absoluteresponse = get_answer(job_id)
        if absoluteresponse == False:
            requests.delete(f"{BASEURL}/generate/text/status/{job_id}")
            continue
        start = absoluteresponse.find("{")
        end = absoluteresponse.find("}")

        if start == -1 or end == -1:
            attempt_generate += 1
            print(f"restart {attempt_generate}")
            continue
        try:
            res = json.loads(absoluteresponse[start:end+1])
        except json.JSONDecodeError:
            attempt_generate += 1
            print(f"restart {attempt_generate}")
            continue

        if res.get("reply") in [i[0] for i in recipes_list]:
            end_time = time.time()
            print(f"Time taken: {round(end_time-start_time)}s")
            for item, id in recipes_list:
                if res.get("reply") == item:
                    res["id"]=id
            res["humanResponse"] = translate_en_to_cs(res.get("humanResponse"))
            return res
        else:
            attempt_generate += 1
            print(f"restart {attempt_generate}")
            requests.delete(f"{BASEURL}/generate/text/status/{job_id}")
            continue


if __name__ == '__main__':
    init_translation()
    domain = ""

    match "demo":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"

    print(domain)
    username = "Admin"
    password = "123456"


    promptmain = ("Chci šťavnatý drink s chutí slunce, pro zvýšení mé mozkové aktivity")
    print(main(promptmain, domain, username, password))
