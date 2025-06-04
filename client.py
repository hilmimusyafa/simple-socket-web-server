import socket
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python client.py <server_host> <server_port> <filename>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        request_line = f"GET /{filename} HTTP/1.1\r\n"
        headers = f"Host: {server_host}:{server_port}\r\n"
        headers += "Connection: close\r\n\r\n"

        http_request = request_line + headers

        client_socket.sendall(http_request.encode())

        response_data = b""
        while True:
            buffer = client_socket.recv(4096)
            if not buffer:
                break
            response_data += buffer

        response_text = response_data.decode(errors="ignore")
        print("\n====== RESPONSE FROM SERVER ======")
        print(response_text)

        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
