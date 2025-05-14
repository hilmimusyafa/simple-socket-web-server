import socket
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: client.py server_host server_port filename")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    request = f"GET /{filename} HTTP/1.1\nHost: {host}\n\n"
    client_socket.send(request.encode())
    
    response = client_socket.recv(4096)
    print(response.decode())
    
    client_socket.close()

if __name__ == "__main__":
    main()
