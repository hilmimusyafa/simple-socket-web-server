import socket
import os

ipServer = '127.0.0.25'
portServer = 5656

def start_server():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((ipServer, portServer))
    serverSocket.listen(1)
    
    print(f"Server berjalan di {ipServer}:{portServer}")

    try:
        while True:
            print("Menunggu koneksi...")
            connectionClient, ipClient = serverSocket.accept()
            print(f"Terhubung dengan {ipClient}")
            
            requestFromClient = connectionClient.recv(1024).decode()
            if not requestFromClient:
                connectionClient.close()
                continue

            requestLine = requestFromClient.splitlines()[0]
            path = requestLine.split()[1]

            if path == "/" or path == "":
                filename = "main.html"
            else:
                filename = path.lstrip("/")

            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    content = f.read()
                responseLine = "HTTP/1.1 200 OK\r\n"
                responseHeader = "Content-Type: text/html\r\n"
                responseHeader += f"Content-Length: {len(content)}\r\n"
                responseHeader += "\r\n"
                connectionClient.sendall(responseLine.encode() + responseHeader.encode() + content)
            else:
                responseLine = "HTTP/1.1 404 Not Found\r\n"
                responseHeader = "Content-Type: text/html\r\n"
                responseBody = "<html><body><h1>404 Not Found</h1></body></html>"
                responseHeader += f"Content-Length: {len(responseBody)}\r\n"
                responseHeader += "\r\n"
                connectionClient.sendall(responseLine.encode() + responseHeader.encode() + responseBody.encode())
            connectionClient.close()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        serverSocket.close()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer berhenti.")