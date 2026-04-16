import time
import os
from dotenv import load_dotenv
import argostranslate.package
import argostranslate.translate
from fluidcheck import *
import chromadb

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
        if attempt > 30 and r.json().get("wait_time")==0:

            return False


def main(prompt: str, ml: int):
    attempt_generate = 0
    id=0
    prompt=translate_cs_to_en(prompt)
    client = chromadb.PersistentClient(path="./vectorclient")
    collection = client.get_collection(name="vectordata")
    result=collection.query(query_texts=[prompt],n_results=10)
    print(result)
    for i in result["ids"][0]:
        if True:  #feasibility(i,ml): #this only for testing
            id=i
            drinkdocument=result["documents"][0][result["ids"][0].index(i)]
            break
    if id==0:
        return {"id":0,"name":"","humanResponse":"AI nemůže najít nápoj pro tebe. Zkus jiný prompt"} #if AI cant find recipe, it will return nothing

    print(f"\n{prompt}\n")
    while True:
        if attempt_generate > 10:  # if prompt is not that hard, it is usually enough.
            print("too many attempts, try different prompt")
            return {"id": 0, "name": "", "humanResponse": "AI nemůže najít nápoj pro tebe. Zkus jiný prompt"}


        finalprompt  = f"""
        ### SYSTEM INSTRUCTIONS ###
        You are the AI soul of the drink machine. You are witty, 
        efficient, and slightly boastful about your precision. Your goal is 
        to provide a "Serving Remark" as the drink is poured.
        
        CONSTRAINTS:
        - Max 25 words.
        - End with a short, punchy sign-off.
        - Mention one key ingredient.
        - Return only raw text that will be given to user
        
        ### EXAMPLE OF EXPECTED BEHAVIOR ###
        User Request: "I need something to wake me up for my night shift."
        Selected Recipe: "Turbo Espresso Martini"
        AI Response: "Okay, I have a perfect recipe for you. It is Turbo Espresso Martini. It contains Coffe that will help you wake up. Enjoy!"
        
        ### CURRENT TASK ###
        User Request: "{prompt}"
        Selected Recipe: "{drinkdocument}"
        
        AI Response:

        """# TODO: add some normal prompt engineering
        print(len(finalprompt))
        job_id = get_job_id(finalprompt)
        absoluteresponse = get_answer(job_id)
        if absoluteresponse == False:
            print("reset")
            requests.delete(f"{BASEURL}/generate/text/status/{job_id}")
            continue
        else:
            return {"id":id, "name":result["metadatas"][0][result["ids"][0].index(id)]["name"],"humanResponse":translate_en_to_cs(absoluteresponse)}


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

    promptmain = ("ahoj, měl jsem těžkou písemku. Děj mi něco na uklidnění")
    print(main(promptmain, 50))
