# File: server_threading.py

import socket
import threading
import os

def handle_client(connection_socket, client_address):
    try:
        request = connection_socket.recv(1024).decode()
        print(f"[REQUEST from {client_address}]")
        # Hanya menampilkan baris pertama request untuk keringkasan log
        print(request.split("\r\n")[0] if "\r\n" in request else request)

        # Parsing HTTP Request
        headers = request.split("\r\n")
        if not headers or not headers[0]:
            # Request kosong atau tidak valid
            print(f"[ERROR] Empty or malformed request from {client_address}")
            # Kirim respons Bad Request jika header tidak ada atau kosong
            error_header = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n'
            error_body = '<h1>400 Bad Request</h1><p>The server received an empty or malformed request.</p>'
            error_response = error_header.encode() + error_body.encode()
            connection_socket.sendall(error_response)
            return

        request_line_parts = headers[0].split()
        if len(request_line_parts) < 2:
            # Request line tidak lengkap
            print(f"[ERROR] Malformed request line from {client_address}: {headers[0]}")
            error_header = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n'
            error_body = '<h1>400 Bad Request</h1><p>The request line is malformed.</p>'
            error_response = error_header.encode() + error_body.encode()
            connection_socket.sendall(error_response)
            return

        filename = request_line_parts[1]

        if filename == '/':
            filename = '/HelloWorld.html'  # default page

        # Keamanan dasar: Mencegah traversal direktori
        # Pastikan filepath aman dan berada dalam direktori yang diharapkan
        base_dir = os.path.abspath(".") # Direktori kerja saat ini
        requested_path = os.path.abspath(os.path.join(base_dir, filename.lstrip('/')))

        if not requested_path.startswith(base_dir):
            # Jika path yang diminta berada di luar direktori dasar, kirim 403 Forbidden
            print(f"[FORBIDDEN] Attempt to access outside base directory from {client_address}: {filename}")
            header = 'HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\n\r\n'
            body = '<h1>403 Forbidden</h1><p>You do not have permission to access this file.</p>'
            response = header.encode() + body.encode()
        elif os.path.isfile(requested_path):
            try:
                with open(requested_path, 'rb') as f:
                    content = f.read()
                header = 'HTTP/1.1 200 OK\r\n'
                # Menentukan Content-Type berdasarkan ekstensi file
                if filename.endswith(".html") or filename.endswith(".htm"):
                    header += 'Content-Type: text/html\r\n'
                elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    header += 'Content-Type: image/jpeg\r\n'
                elif filename.endswith(".png"):
                    header += 'Content-Type: image/png\r\n'
                elif filename.endswith(".css"):
                    header += 'Content-Type: text/css\r\n'
                elif filename.endswith(".js"):
                    header += 'Content-Type: application/javascript\r\n'
                elif filename.endswith(".gif"):
                    header += 'Content-Type: image/gif\r\n'
                elif filename.endswith(".txt"):
                    header += 'Content-Type: text/plain\r\n'
                else:
                    header += 'Content-Type: application/octet-stream\r\n'

                header += f'Content-Length: {len(content)}\r\n'
                header += 'Connection: close\r\n' # Menambahkan header Connection: close
                header += '\r\n'
                response = header.encode() + content
            except IOError as e:
                print(f"[ERROR] Could not read file {requested_path}: {e}")
                header = 'HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n'
                body = '<h1>500 Internal Server Error</h1><p>The server encountered an error reading the file.</p>'
                response = header.encode() + body.encode()
        else:
            print(f"[NOT FOUND] File not found {requested_path} requested by {client_address}")
            header = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n'
            body = '<h1>404 Not Found</h1><p>The requested file was not found on this server.</p>'
            response = header.encode() + body.encode()

        connection_socket.sendall(response)
    except IndexError:
        print(f"[ERROR] Malformed HTTP request (IndexError) from {client_address}. Request: {request[:100]}...") # Log sebagian request
        error_header = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n'
        error_body = '<h1>400 Bad Request</h1><p>The server could not understand the request due to invalid syntax.</p>'
        try:
            connection_socket.sendall(error_header.encode() + error_body.encode())
        except Exception as e_send:
            print(f"[ERROR] Could not send 400 error response: {e_send}")
    except socket.error as e:
        print(f"[SOCKET ERROR] {e} for {client_address}")
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e} for {client_address}")
        error_header = 'HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n'
        error_body = '<h1>500 Internal Server Error</h1><p>The server encountered an unexpected condition.</p>'
        try:
            connection_socket.sendall(error_header.encode() + error_body.encode())
        except Exception as e_send:
            print(f"[ERROR] Could not send 500 error response: {e_send}")
    finally:
        connection_socket.close()
        print(f"[DISCONNECTED] {client_address}")


def start_server(host='0.0.0.0', port=6789):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((host, port))
    except socket.error as e:
        print(f"[FATAL ERROR] Could not bind to address {host}:{port} - {e}. Check if the port is already in use or if you have permissions.")
        return # Keluar jika bind gagal

    server_socket.listen(5)
    print(f"[STARTED] Server listening on http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}")
    print(f"Default file is HelloWorld.html. Access via http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}/")

    try:
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"\n[CONNECTED] Accepted connection from {client_address}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
            except socket.error as e:
                # Menangani error pada accept() jika server socket ditutup secara tiba-tiba
                print(f"[SERVER SOCKET ERROR] Could not accept connection: {e}")
                break # Keluar dari loop jika socket server bermasalah
    except KeyboardInterrupt:
        print("\n[STOPPING] Server shutting down due to KeyboardInterrupt...")
    except Exception as e:
        print(f"\n[UNEXPECTED SERVER ERROR] {e}")
    finally:
        print("[CLOSING] Closing server socket.")
        server_socket.close()
        print("[SHUTDOWN] Server has been shut down.")

if __name__ == "__main__":
    # Membuat file HelloWorld.html default jika belum ada, untuk kemudahan testing
    if not os.path.exists("HelloWorld.html"):
        with open("HelloWorld.html", "w") as f:
            f.write("<!DOCTYPE html><html><head><title>Default Page</title></head><body><h1>Hello from Default Page!</h1><p>This server is working.</p></body></html>")
        print("[INFO] Created default HelloWorld.html")
    start_server()