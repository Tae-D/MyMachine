import requests
import time
import json

BASEURL= "https://aihorde.net/api/v2"
API_KEY = "WqioktBxymwd88nxXpuvAQ"




def get_job_id(prompt:str):
    urlai=f"{BASEURL}/generate/text/async"
    payload = {"n":1,"max_length": 10000,"prompt":prompt}#todo: Make AI answer longer
    headers ={}
    if API_KEY:
        headers["apikey"] = API_KEY
    response= requests.post(urlai, json=payload, headers=headers)

    if response.status_code!=200 and response.status_code!=202:
        print(f"error code: {response.status_code}, error message: {response.text}")
        exit(response.status_code)
    print(response.json())
    job_id=response.json().get("id")
    return job_id

def get_answer(job):
    status_url = f"{BASEURL}/generate/text/status/{job}"
    attempt=0
    while True:
        r = requests.get(status_url)
        if r.status_code!=200 and r.status_code!=202:
            print(f"error code: {r.status_code}, error message: {r.text}")

        if r.json().get("finished"):
            absoluteresponse=r.json()["generations"][0]["text"]
            return absoluteresponse
        time.sleep(2)
        attempt+=1
        print(r.json().get("wait_time"),r.json().get("is_possible"))

        if attempt>30:
            print("too many attempts")
            return False

def main(prompt:str, urlrecipe:str, headersrecipefunc):

    attempt_generate=0
    start_time = time.time()

    recipeconnectioncode=requests.get(urlrecipe, headers=headersrecipefunc)
    if recipeconnectioncode.status_code ==200:
        recipes=recipeconnectioncode.json()
    else:
        print(f"Couldn't connect to recipe database, try again later. Error code: {recipeconnectioncode.status_code}")
        exit(2)

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

        finalprompt = f"{system_instruction}\n\n{example}\n\nInput: {prompt}\nOutput:" #Horrible prompt building
        job_id=get_job_id(finalprompt)
        absoluteresponse=get_answer(job_id)
        if absoluteresponse==False:
            print("too many attempts")
            continue
        start=absoluteresponse.find("{")
        end=absoluteresponse.find("}")

        if start==-1 or end==-1:
            print(f"bad json response TEXT: {absoluteresponse}")
            continue
        try:
            res = json.loads(absoluteresponse[start:end+1])
        except json.JSONDecodeError:
            print(f"AI sent broken JSON TEXT: {absoluteresponse}")
            continue
        recipes_list=[recipes["content"][i]["name"] for i in range(len(recipes["content"]))]
        if res.get("reply") in recipes_list:
            print(res)
            print(res.get("reply"))
            end_time=time.time()
            print(f"Time taken: {round(end_time-start_time)}s")
            return res
        else:
            attempt_generate+=1
            if attempt_generate>3:
                print("too many attempts, try diferent prompt")
                exit()
            else:
                print(f"drink is not detected TEXT: {absoluteresponse}")#sometimes it just spams random things in there
                continue

if __name__ == '__main__':
    url="https://demo.cocktailpi.org/api/recipe/?page=1&inCategory=1"
    headersrecipe={"Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzY2NDA3Mjc2LCJleHAiOjE3NjY0OTM2NzYsInJlbWVtYmVyIjpmYWxzZX0.ltFexg4xpnWV1nuik7ZKw9-oYAozzzf0YJlXxDgzooCnv4bvu_U6unKEFDf8Txz9yOcrMAqfRM6cdzTN8mBnbA"}

    promptmain=("Dostal jsem špatnou známku z testu")

    main(promptmain,url,headersrecipe)