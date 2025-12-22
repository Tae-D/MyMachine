import requests
import time
import json

BASEURL= "https://aihorde.net/api/v2"
API_KEY = "WqioktBxymwd88nxXpuvAQ"

headersrecipe = {
    "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzY2NDA3Mjc2LCJleHAiOjE3NjY0OTM2NzYsInJlbWVtYmVyIjpmYWxzZX0.ltFexg4xpnWV1nuik7ZKw9-oYAozzzf0YJlXxDgzooCnv4bvu_U6unKEFDf8Txz9yOcrMAqfRM6cdzTN8mBnbA"
}


def get_job_id(prompt:str):
    url=f"{BASEURL}/generate/text/async"
    payload = {"n":1,"max_length": 700,"prompt":prompt}
    headers ={}
    if API_KEY:
        headers["apikey"] = API_KEY
    response= requests.post(url, json=payload, headers=headers)

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
        print(r.json().get("wait_time"))
        if r.status_code!=200 and r.status_code!=202:
            print(f"error code: {r.status_code}, error message: {r.text}")
        if r.json().get("finished"):
            absoluteresponse=r.json()["generations"][0]["text"]
            return absoluteresponse
        time.sleep(1)
        attempt+=1
        if attempt>30:
            print("too many attempts")
            return False

def main(prompt:str):
    while True:
        recipeconnectioncode=requests.get("https://demo.cocktailpi.org/api/recipe/?page=1&inCategory=1",headers=headersrecipe)
        if recipeconnectioncode.status_code ==200:
            print("connected to recipe database")
            recipes=recipeconnectioncode.json()
        else:
            print(f"Couldn't connect to recipe database, try again later. Error code: {recipeconnectioncode.status_code}")

        system_instruction = (
            f"You are a drink machine API. Respond ONLY in valid dictionary. Take one drink from {recipes}. "
            "The JSON must contain three keys: 'reply', 'suggestedRecipeId', and 'reasoningSummary'."
        )
        example = (
            "Example Input: 'I am thirsty'\n"
            "Example Output: {\"reply\": \"Rockshandy\", \"suggestedRecipeId\": 251, \"reasoningSummary\": \"User needs something against thirst.\"}"
        )

        finalprompt = f"{system_instruction}\n\n{example}\n\nInput: {prompt}\nOutput:"
        job_id=get_job_id(finalprompt)
        absoluteresponse=get_answer(job_id)
        if absoluteresponse==False:
            pass
        start=absoluteresponse.find("{")
        end=absoluteresponse.find("}")
        if start==-1 or end==-1:
            pass
        else:
            res = json.loads(absoluteresponse[start:end+1])
            print(res)
            return(res)

if __name__ == '__main__':
    main("Dej mi něco bez cukru")