import socket
import threading
import json
import sys
import queue

from styles.colors import Colors

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 5000

# Armazenamento para os dois clientes
clients = []
client_info = {}

def handle_client(client_socket, address):
    print(f"{Colors.GREEN}[+]{Colors.RESET} New connection: {Colors.YELLOW}{address}{Colors.RESET}")
    clients.append(client_socket)
    client_sent_leave_message = False  # Flag para controlar se o cliente já enviou mensagem de saída
    
    try:
        # Receber informações iniciais (nickname e chave pública)
        init_data = client_socket.recv(4096)
        if not init_data:
            return
            
        init_info = json.loads(init_data.decode())
        nickname = init_info.get('nickname', 'anonymous')
        public_key = init_info.get('public_key')
        
        # Armazenar informações do cliente
        client_info[client_socket] = {
            'nickname': nickname,
            'public_key': public_key,
            'address': address
        }
        
        print(f"{Colors.GREEN}[*]{Colors.RESET} Registered {Colors.YELLOW}{nickname}@{address}{Colors.RESET} client.")
        
        if len(clients) == 2:
            client1 = clients[0]
            client2 = clients[1]
            
            client1_data = json.dumps({
                'nickname': client_info[client2]['nickname'],
                'public_key': client_info[client2]['public_key']
            })
            client1.send(client1_data.encode())
            
            client2_data = json.dumps({
                'nickname': client_info[client1]['nickname'],
                'public_key': client_info[client1]['public_key']
            })
            client2.send(client2_data.encode())
            
            print(f"{Colors.GREEN}[*]{Colors.RESET} Complete key exchange between the two clients!")
        
        while True:
            message_data = client_socket.recv(8192)
            if not message_data:
                break
                
            try:
                # Verifica se é uma mensagem de sistema de saída
                message_obj = json.loads(message_data.decode())
                if 'system' in message_obj and 'message' in message_obj and 'leave' in message_obj['message']:
                    client_sent_leave_message = True
                    print(f"{Colors.YELLOW}[*]{Colors.RESET} {Colors.YELLOW}{nickname}{Colors.RESET} sent leave message")
            except:
                pass
                
            if len(clients) > 1:
                other_client = clients[1] if client_socket == clients[0] else clients[0]
                try:
                    try:
                        # Tenta exibir uma prévia da mensagem encaminhada
                        print(f"{Colors.BLUE}[*]{Colors.RESET} {Colors.YELLOW}{nickname}{Colors.RESET} -> {Colors.YELLOW}{client_info[other_client]['nickname']}: {message_data}{Colors.RESET}")
                    except:
                        pass
                        
                    other_client.send(message_data)
                except Exception as e:
                    print(f"{Colors.RED}[!]{Colors.RESET} Error forwarding message: {e}")
                    break
            else:
                print(f"{Colors.YELLOW}[!]{Colors.RESET} Another client is not connected, message not sent")
                
    except Exception as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Error processing client {address}: {e}")
    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in client_info:
            nickname = client_info[client_socket]['nickname']
            del client_info[client_socket]
            
        try:
            client_socket.close()
        except:
            pass
            
        print(f"{Colors.RED}[-]{Colors.RESET} Disconected {Colors.YELLOW}{nickname}@{address}{Colors.RESET} client")
        
        # Só envia mensagem de saída se o cliente não tiver enviado uma explicitamente
        if clients and not client_sent_leave_message:
            try:
                system_message = json.dumps({
                    'system': True,
                    'message': f"{nickname} leave."
                })
                clients[0].send(system_message.encode())
            except:
                pass

def check_exit_command(command_queue):
    while True:
        command = input()
        command_queue.put(command.strip().lower())
        if command.strip().lower() == "exit":
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)
    
    print(f"{Colors.CYAN}[*] Server listening on {Colors.YELLOW}{HOST}:{PORT}{Colors.RESET}")
    
    command_queue = queue.Queue()
    command_thread = threading.Thread(target=check_exit_command, args=(command_queue,), daemon=True)
    command_thread.start()
    
    # Configurar timeout para verificar comandos periodicamente
    server.settimeout(1.0)
    
    running = True
    try:
        while running and len(clients) < 2:
            try:
                # Verificar comandos
                if not command_queue.empty():
                    command = command_queue.get()
                    if command == "exit":
                        running = False
                        break
                
                # Aceitar conexão
                client_socket, address = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print(f"{Colors.YELLOW}[!] Keyboard interrupt!{Colors.RESET}")
                running = False
                break
        
        while running and clients:
            try:
                if not command_queue.empty():
                    command = command_queue.get()
                    if command == "exit":
                        running = False
                        break
            except KeyboardInterrupt:
                print(f"{Colors.YELLOW}[!] Keyboard interrupt!{Colors.RESET}")
                running = False
                break
                
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
    finally:
        print(f"{Colors.YELLOW}[!] Shuting down...{Colors.RESET}")
        for client in clients[:]:
            try:
                client.close()
            except:
                pass
        server.close()
        print(f"{Colors.GREEN}[*] Server closed.{Colors.RESET}")

if __name__ == "__main__":
    main()
