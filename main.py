import socket
import threading
import json
import os

class ChatServer:
    def __init__(self, host='0.0.0.0', port=int(os.environ.get('PORT', 5005))):
        self.host = host
        self.port = port
        self.clients = {}
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f"✅ RedHack Sunucu çalışıyor: {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
    
    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(4096).decode()
            if data:
                login = json.loads(data)
                if login.get("tip") == "kayit":
                    username = login["kullanici"]
                    self.clients[client_socket] = username
                    print(f"👤 {username} bağlandı! Toplam: {len(self.clients)}")
                    
                    while True:
                        data = client_socket.recv(65536).decode()
                        if not data:
                            break
                        message = json.loads(data)
                        if message["tip"] == "mesaj":
                            if message["alici"] == "genel":
                                self.broadcast(message, client_socket)
                            else:
                                self.private_message(message["alici"], message)
        except:
            pass
        finally:
            if client_socket in self.clients:
                username = self.clients[client_socket]
                del self.clients[client_socket]
                print(f"👋 {username} ayrıldı! Kalan: {len(self.clients)}")
            client_socket.close()
    
    def broadcast(self, message, exclude_socket=None):
        for client in self.clients:
            if client != exclude_socket:
                try:
                    client.send(json.dumps(message).encode())
                except:
                    pass
    
    def private_message(self, recipient, message):
        for client, username in self.clients.items():
            if username == recipient:
                try:
                    client.send(json.dumps(message).encode())
                except:
                    pass

if __name__ == "__main__":
    server = ChatServer()
    server.start()
