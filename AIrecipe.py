import requests
import time
import json

BASEURL = "https://aihorde.net/api/v2"
API_KEY = "WqioktBxymwd88nxXpuvAQ"


def get_job_id(prompt: str):
    urlai = f"{BASEURL}/generate/text/async"
    payload = {"n": 1, "params": {"max_length": 300}, "prompt": prompt}
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
        if attempt > 30 or r.json().get("wait_time") > 70:
            return False


def main(prompt: str, urlrecipe: str, headersrecipefunc):

    attempt_generate = 0
    start_time = time.time()

    recipeconnectioncode = requests.get(urlrecipe, headers=headersrecipefunc)
    if recipeconnectioncode.status_code == 200:
        recipes = recipeconnectioncode.json()
    else:
        print(
            f"Couldn't connect to recipe database, try again later. Error code: {recipeconnectioncode.status_code}")
        exit(2)
    print(f"\n{prompt}\n")
    while True:

        system_instruction = (
            f"You are a drink machine API. Respond ONLY in valid dictionary. Take one drink from {recipes}. "
            "The dictionary must contain four keys: 'reply', 'suggestedRecipeId',  'reasoningSummary', 'humanResponse'."
            "humanResponse should be a comment in Czech for drink, that is chosen"

        )
        example = (
            "Example Input: 'I am thirsty'\n"
            "Example Output: {\"reply\": \"Rockshandy\", \"suggestedRecipeId\": 251, \"reasoningSummary\": \"User needs something against thirst.\", \"humanResponse\": \"Tady je tvoje Rockshandy, obsahuje citrónovou sodu, která je výborná proti žízni\"}"
        )

        # Horrible prompt building
        finalprompt = f"{system_instruction}\n\n{example}\n\nInput: {prompt}\nOutput:"
        job_id = get_job_id(finalprompt)
        absoluteresponse = get_answer(job_id)
        if absoluteresponse == False:
            continue
        start = absoluteresponse.find("{")
        end = absoluteresponse.find("}")

        if start == -1 or end == -1:
            attempt_generate += 1
            continue
        try:
            res = json.loads(absoluteresponse[start:end+1])
        except json.JSONDecodeError:
            continue
        recipes_list = [recipes["content"][i]["name"]
                        for i in range(len(recipes["content"]))]
        if res.get("reply") in recipes_list:
            print(res)
            end_time = time.time()
            print(f"Time taken: {round(end_time-start_time)}s")
            return res
        else:
            attempt_generate += 1
            if attempt_generate > 5:  # if prompt is not that hard, it is usually enough.
                print("too many attempts, try different prompt")
                end_time = time.time()
                print(f"Time taken: {round(end_time-start_time)}s")
                exit()
            else:
                continue


if __name__ == '__main__':
    domain = ""

    match "local":
        case "local":
            domain = "http://localhost:8080"
        case "demo":
            domain = "https://demo.cocktailpi.org"

    url = f"{domain}/api/recipe/?page=1&inCategory=1"
    authurl = f"{domain}/api/auth/login"
    token = (requests.post(authurl, json={
             "username": "Admin", "password": "123456", "remember": "true"}))
    headersrecipe = {"Authorization": f"Bearer {token.json()["accessToken"]}"}

    promptmain = ("Měl jsem těžkou písemku")
    main(promptmain, url, headersrecipe)
