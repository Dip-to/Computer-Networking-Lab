import requests
fil=input('Enter File Name: ')
x = requests.get('http://localhost:8080//Users/syedmumtahinmahmud/Desktop/Class/networking/netlab3/B/a.txt')
if x.status_code == 200:
    with open(fil, "wb") as f:
        f.write(x.content)
    print("File successfully received")
    print("Content: ",x.text)
else:
    print("Error: Could not receive file")