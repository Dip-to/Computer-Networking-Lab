import os
import socket
import threading

IP = ''
PORT = 4491
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        print(cmd)

        if cmd == "list":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "upload":
            name, text = data[1], data[2]
            print(name)
            filepath = os.path.join(SERVER_DATA_PATH, name)
            with open(filepath, "w") as f:
                f.write(text)

            send_data = "OK@File uploaded successfully."
            conn.send(send_data.encode(FORMAT))
            
        elif cmd == "download":
            path = data[1]
            print(path)
            with open(f"{path}", "r") as f:
                text = f.read()
                print(text)
            filename = path.split("/")[-1]
            send_data = f"{cmd}@{filename}@{text}"
            conn.send(send_data.encode(FORMAT))

            send_data = "OK@File downloaded successfully."
            conn.send(send_data.encode(FORMAT))



        

        elif cmd == "bye":
            break
        
    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()