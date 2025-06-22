
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

## How to Verify Encryption with Wireshark

To confirm that end-to-end encryption (E2EE) is working correctly and that the server cannot read the message contents, follow these steps using Wireshark:

- Start Wireshark:
    - Open Wireshark before starting the chat;
    - Select the correct network interface:
        - If testing locally, choose Npcap Loopback Adapter (Windows) or lo0 (macOS/Linux);
        - If using two devices, use the real network interface (e.g., Wi-Fi).

- Apply a capture filter
    ```bash
    tcp.port==5000

- Start the server and clients
    - Connect two clients and send some test messages between them.

- Inspect the captured packets
    - Look for packets containing data and session_key;
    - Expand the TCP stream and you'll see the encrypted payload;
    - ✅ If the payload looks like random characters (base64 or binary) and does not contain phrases like "Hello" or "Oi", encryption is confirmed.

## Autors

- [Rebeca Amorim](https://www.github.com/Rebeusca)