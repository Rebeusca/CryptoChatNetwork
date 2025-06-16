import socket
import threading
import json
import base64
from tkinter import simpledialog, messagebox, Tk

from colors.colors import Colors
from utils_crypto import (
    generate_key_pair, 
    serialize_public_key, 
    deserialize_public_key, 
    encrypt_key, 
    decrypt_session_key,
    generate_session_key,
    encrypt_message,
    decrypt_message
)
from gui.chat_window import ChatWindow

# Porta padrão para conexão
PORT = 5000

# Flag global para controlar exibição de mensagens de erro
show_connection_errors = True

def receive_messages(sock, private_key, session_key, peer_nickname):
    global show_connection_errors
    
    while True:
        try:
            data = sock.recv(8192)
            if not data:
                # The other user has disconnected - don't show error if we're voluntarily exiting
                if show_connection_errors:
                    print(f"{Colors.YELLOW}[SYSTEM] The other user has left the chat.{Colors.RESET}")
                break
                
            # Tentativa de descriptografar a mensagem
            try:
                encrypted_data = json.loads(data.decode())
                
                # Verifica se é uma mensagem criptografada
                if 'encrypted_message' in encrypted_data and 'encrypted_key' in encrypted_data:
                    # Primeiro descriptografa a chave de sessão usando nossa chave privada
                    encrypted_session_key = base64.b64decode(encrypted_data['encrypted_key'])
                    message_session_key = decrypt_session_key(private_key, encrypted_session_key)
                    
                    # Agora descriptografa a mensagem com a chave de sessão recebida
                    encrypted_message = base64.b64decode(encrypted_data['encrypted_message'])
                    plaintext = decrypt_message(message_session_key, encrypted_message)
                    
                    # Exibe a mensagem descriptografada
                    print(f"{Colors.GREEN}[{peer_nickname}]{Colors.RESET}: {Colors.CYAN}{plaintext}{Colors.RESET}")
                    
                # Se for uma mensagem do sistema
                elif 'system' in encrypted_data:
                    print(f"{Colors.YELLOW}[SYSTEM] {encrypted_data.get('message', 'The other user has left the chat.')}{Colors.RESET}")
            
            except Exception as e:
                # Only show processing errors if we're not voluntarily exiting
                if show_connection_errors:
                    # Don't show connection-related errors
                    if "message" not in str(e).lower() and "connection" not in str(e).lower():
                        pass  # Suppress all processing errors for better user experience
                
        except Exception as e:
            # Don't show error if we're voluntarily exiting or if it's a connection error 
            if show_connection_errors and "10053" not in str(e) and "connection" not in str(e).lower():
                print(f"{Colors.YELLOW}[SYSTEM] Connection lost.{Colors.RESET}")
            break

def connect_to_server(server_ip, port=5000, nickname=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print(f"{Colors.CYAN}[*] Connecting to server at {Colors.YELLOW}{server_ip}:{port}{Colors.RESET}...")
        client.connect((server_ip, port))
        print(f"{Colors.GREEN}[+] Connected to server successfully!{Colors.RESET}")
        
        # Gerar par de chaves para criptografia E2EE
        private_key, public_key = generate_key_pair()
        public_key_pem = serialize_public_key(public_key)
        
        # Se o nickname não foi fornecido, solicite ao usuário
        if nickname is None:
            nickname = input(f"{Colors.CYAN}Enter your nickname: {Colors.YELLOW}")
            print(Colors.RESET, end="")
        
        # Enviar informações iniciais para o servidor
        init_data = {
            'nickname': nickname,
            'public_key': public_key_pem.decode()
        }
        
        client.send(json.dumps(init_data).encode())
        print(f"{Colors.GREEN}[*] Connected as {Colors.BOLD}{nickname}{Colors.RESET}.")
        
        # Aguardar a conexão do outro cliente e receber sua chave pública
        print(f"{Colors.CYAN}[*] Waiting for another user...{Colors.RESET}")
        peer_data = client.recv(4096)
        
        try:
            peer_info = json.loads(peer_data.decode())
            
            peer_nickname = peer_info['nickname']
            # Convertemos de string para bytes e depois para objeto de chave
            peer_public_key = deserialize_public_key(peer_info['public_key'].encode())
            
            print(f"{Colors.GREEN}[+] {peer_nickname} connected to chat! Type your messages below!{Colors.RESET}")
            
            # Criamos uma chave de sessão única para esta conversa
            session_key = generate_session_key()
            return client, nickname, peer_nickname, private_key, public_key, peer_public_key, session_key
            
        except Exception as e:
            # Tratando caso de resposta do servidor que não é relativa a outro usuário
            if 'system' in str(peer_data.decode()):
                print(f"{Colors.YELLOW}[SYSTEM] Message from server: {str(peer_data.decode())}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[SYSTEM] Waiting for another user...{Colors.RESET}")
            
            # Não levanta exceção, mas retorna None para indicar falha
            client.close()
            return None, None, None, None, None, None, None
        
    except ConnectionRefusedError:
        print(f"{Colors.RED}[!] Error connecting: The server refused the connection. Check if the server is running.{Colors.RESET}")
        return None, None, None, None, None, None, None
    except socket.gaierror:
        print(f"{Colors.RED}[!] Error connecting: Invalid IP address or DNS problem.{Colors.RESET}")
        return None, None, None, None, None, None, None
    except TimeoutError:
        print(f"{Colors.RED}[!] Error connecting: Connection timed out. Check the IP address and if the server is running.{Colors.RESET}")
        return None, None, None, None, None, None, None
    except Exception as e:
        print(f"{Colors.RED}[!] Error connecting: {str(e)}{Colors.RESET}")
        return None, None, None, None, None, None, None

def send_encrypted_message(sock, message, peer_public_key, session_key):
    try:
        encrypted_session_key = encrypt_key(peer_public_key, session_key)
        encrypted_message = encrypt_message(session_key, message)
        
        data = {
            'encrypted_key': base64.b64encode(encrypted_session_key).decode(),
            'encrypted_message': base64.b64encode(encrypted_message).decode()
        }
        
        sock.send(json.dumps(data).encode())
        return True
            
    except Exception as e:
        # Avoid showing technical errors to the user
        if show_connection_errors:
            print(f"{Colors.YELLOW}[SYSTEM] Could not send message. The other user may have disconnected.{Colors.RESET}")
        return False

def main():
    global show_connection_errors
    
    # Inicializar o Tkinter corretamente
    root = Tk()
    root.withdraw()  # Esconde a janela principal temporariamente
    
    try:
        # Solicita o endereço IP do servidor usando Tkinter dialog
        server_ip = simpledialog.askstring("Cryptochat", "Enter server IP address:", initialvalue="127.0.0.1")
        if not server_ip:
            root.destroy()  # Fecha a janela Tk se o usuário cancelar
            return  # Usuário cancelou
        
        # Solicita o nickname
        nickname = simpledialog.askstring("Cryptochat", "Enter your nickname:")
        if not nickname:
            root.destroy()  # Fecha a janela Tk se o usuário cancelar
            return  # Usuário cancelou
            
        # Tenta conectar ao servidor e configurar a criptografia E2EE
        client, nickname, peer_nickname, private_key, public_key, peer_public_key, session_key = connect_to_server(server_ip, PORT, nickname)
        
        # Verifica se a conexão foi bem-sucedida
        if client is None:
            messagebox.showerror("Error", "Failed to connect to the server.")
            root.destroy()
            return
            
        # Destruir a janela temporária, vamos criar a janela de chat
        root.destroy()
        
        # Criando a janela de chat
        def on_send_message(message):
            # Mostra a mensagem que você está enviando
            chat_window.display(f"[You]: {message}")
            
            # Envia a mensagem criptografada para o outro cliente
            if not send_encrypted_message(client, message, peer_public_key, session_key):
                chat_window.display("[SYSTEM] Failed to send message. The other user may have disconnected.")
        
        def on_close_window():
            global show_connection_errors
            show_connection_errors = False
            
            if client:
                try:
                    # Enviar mensagem de despedida
                    system_message = {
                        'system': True,
                        'message': f"{nickname} leave."
                    }
                    client.send(json.dumps(system_message).encode())
                except:
                    pass
                    
                # Fecha a conexão silenciosamente
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                    
                try:
                    client.close()
                except:
                    pass
        
        # Criando a janela de chat
        chat_window = ChatWindow(nickname, on_send_message, on_close_window)
        chat_window.display(f"[SYSTEM] Connected as {nickname}.")
        chat_window.display(f"[SYSTEM] {peer_nickname} is connected to chat!")
        
        # Função para receber mensagens e exibi-las na interface gráfica
        def receive_messages_gui():
            global show_connection_errors
            
            while show_connection_errors:
                try:
                    data = client.recv(8192)
                    if not data:
                        # O outro usuário se desconectou
                        if show_connection_errors:
                            chat_window.display("[SYSTEM] The other user has left the chat.")
                        break
                        
                    # Tentativa de descriptografar a mensagem
                    try:
                        encrypted_data = json.loads(data.decode())
                        
                        # Verifica se é uma mensagem criptografada
                        if 'encrypted_message' in encrypted_data and 'encrypted_key' in encrypted_data:
                            # Primeiro descriptografa a chave de sessão usando nossa chave privada
                            encrypted_session_key = base64.b64decode(encrypted_data['encrypted_key'])
                            message_session_key = decrypt_session_key(private_key, encrypted_session_key)
                            
                            # Agora descriptografa a mensagem com a chave de sessão recebida
                            encrypted_message = base64.b64decode(encrypted_data['encrypted_message'])
                            plaintext = decrypt_message(message_session_key, encrypted_message)

                            print(f"{Colors.GREEN}[{peer_nickname}]{Colors.RESET}: {Colors.CYAN}{encrypted_data}{Colors.RESET}")
                            
                            # Exibe a mensagem descriptografada na interface
                            chat_window.display(f"[{peer_nickname}]: {plaintext}")
                            
                        # Se for uma mensagem do sistema
                        elif 'system' in encrypted_data:
                            chat_window.display(f"[SYSTEM] {encrypted_data.get('message', 'The other user has left the chat.')}")
                    
                    except Exception as e:
                        # Só exibe erro de processamento se não estamos saindo voluntariamente
                        if show_connection_errors:
                            pass  # Não mostramos erros técnicos na interface
                        
                except Exception as e:
                    # Não exibe erro se estivermos saindo voluntariamente
                    if show_connection_errors and "10053" not in str(e) and "connection" not in str(e).lower():
                        chat_window.display("[SYSTEM] Connection lost.")
                    break
        
        # Inicia a thread para receber mensagens
        receiver_thread = threading.Thread(target=receive_messages_gui, daemon=True)
        receiver_thread.start()
        
        # Inicia o loop principal da interface gráfica
        chat_window.run()
        
    except Exception as e:
        import traceback
        print(f"Error in main: {e}")
        print(traceback.format_exc())
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        if 'root' in locals() and root.winfo_exists():
            root.destroy()

if __name__ == "__main__":
    print("Starting Cryptochat client...")
    try:
        main()
    except Exception as e:
        import traceback
        print(f"Error in main(): {e}")
        print(traceback.format_exc())
        input("Press Enter to exit...")
