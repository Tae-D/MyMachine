import AIrecipe
import time
promptmain = ("Čeká mě těžká písemka, chtěl bych drink pro uklidnění. Mám alergii na jahody")
repeats=20
times=[]
drinks=[]
amount={}
username = "Admin"
password = "123456"
domain = "http://localhost:8080"

for i in range(repeats):
    start = time.time()
    response=AIrecipe.main(promptmain, domain, username, password)
    end = time.time()
    times.append(end-start)
    drinks.append(response["reply"])
    print(f"{i}/{repeats}")
    print(drinks)
    print(times)
    print(f"průměr: {sum(times) / len(times)}") #průměr: 51.149335992336276

for drink in drinks:
    amount[drink]= amount.get(drink, 0)+1 #{'Champagne Comme-il-faut': 1, 'The Ella': 9, 'Virgin Piña Colada': 1, 'Virgin Mojito': 2, 'Sunset': 1, 'Tropical Cooler': 5, 'Keep Sober': 1}

print(amount)