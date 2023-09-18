import socket
import os

IP = '10.33.2.92'
PORT = 4491
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
server_download="dowload"


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "help":
            client.send(cmd.encode(FORMAT))
        elif cmd == "bye":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "list":
            client.send(cmd.encode(FORMAT))
      
        elif cmd == "upload":
            path = data[1]

            with open(f"{path}", "r") as f:
                text = f.read()

            filename = path.split("/")[-1]
            send_data = f"{cmd}@{filename}@{text}"
            client.send(send_data.encode(FORMAT))

        
        elif cmd == "download":
            tt=str(data[1])
            s=f"{cmd}@{tt}"
            client.send(s.encode(FORMAT))
            rcv=client.recv(SIZE).decode(FORMAT)
            rcv=rcv.split("@")
            name, text = rcv[1], rcv[2]
            filepath = os.path.join('dowload', name)
            with open(filepath, "w") as f:
                f.write(text)
                f.close()
            print("downloaded")
            continue

            


    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()