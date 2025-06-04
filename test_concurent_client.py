import socket
import threading
import time

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 6789       
FILENAME_TO_REQUEST = 'hello.html'
NUM_CLIENTS = 5

def client_task(client_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[Client {client_id}] Connected to server.")

        request_line = f"GET /{FILENAME_TO_REQUEST} HTTP/1.1\r\n"
        headers = f"Host: {SERVER_HOST}:{SERVER_PORT}\r\n"
        headers += "Connection: close\r\n\r\n" 
        http_request = request_line + headers

        client_socket.sendall(http_request.encode())
        print(f"[Client {client_id}] Request sent.")

        response_data = b""
        start_time = time.time()
        while True:
            buffer = client_socket.recv(4096)
            if not buffer:
                break
            response_data += buffer
            if time.time() - start_time > 10: 
                print(f"[Client {client_id}] Timeout waiting for response.")
                break
        
        response_text = response_data.decode(errors="ignore")
        print(f"[Client {client_id}] Response received (first 100 chars): {response_text[:100].replace(r'\r\n', ' ')}...")
        client_socket.close()
        print(f"[Client {client_id}] Connection closed.")

    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

if __name__ == "__main__":
    threads = []
    print(f"Starting {NUM_CLIENTS} client threads to connect to {SERVER_HOST}:{SERVER_PORT}...")
    for i in range(NUM_CLIENTS):
        thread = threading.Thread(target=client_task, args=(i+1,))
        threads.append(thread)
        thread.start()
        time.sleep(0.05) 

    for thread in threads:
        thread.join() 

    print("All client threads finished.")