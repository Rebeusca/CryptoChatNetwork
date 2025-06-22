
# 🔐 CryptoChat

CryptoChat is a secure chat application that uses TCP socket communication and end-to-end encryption (E2EE) between two clients, guaranteeing total privacy in the exchange of messages. Even the server has no access to the content of the conversations.

## How to run locally:

**Option 1: using Python (`.py` files)**

    1. Navigate to the project directory;

    2. Run the launcher:

            python launcher.py

    3. In the interface:

        - Click Start Server;

        - Then click Open Client;

        - Enter the IP address (local or public) and a name for Client 1;

        - Repeat to open Client 2.

**Option 2: using executable (.exe files)**

    1. Go to the dist/ folder;

    2. Double-click launcher.exe;

    3. Follow the same interface steps as above.
    
## Technologies used:

- Python 3.12
- Tkinter (GUI)
- Cryptography (RSA + Fernet)
- Sockets TCP
- PyInstaller

## Functionalities:

- WhatsApp/Signal-style hybrid encryption (RSA + AES)
- Intuitive graphical interface
- Practical security validation with Wireshark sniffing
- One-click launcher to start server and clients


## Security tests:

- Messages captured via Wireshark appear fully encrypted (unreadable);
- Only the recipient client is able to decrypt the message;
- The server relays messages without ever accessing their content.

## Autors

- [Rebeca Amorim](https://www.github.com/Rebeusca)