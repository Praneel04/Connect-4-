import socket
import csv
import threading
import pickle
import ssl
# Constants
HOST = 'localhost'  # Localhost
PORT = 5559  # Port to listen on
MAX_CONNECTIONS = 2  # Maximum number of clients
CERTIFICATE_FILE = 'localhost.crt'
KEY_FILE = 'localhost.key' 
# Global variables
clients = []
player_turn = 0
game_over = False
board = [[0] * 7 for _ in range(6)]  # 6x7 board
row_count=[0,0,0,0,0,0,0]
moves_completed = 0  # Count of completed moves


def handle_client(client, player):
    #THis funciton handles the clients and their moves.
    global player_turn
    global game_over
    iter=0
    while not game_over:
        try:
            data = client.recv(1024).decode()
            print(data)
            #recieves the move
            if data == 'QUIT':
                break
            
            if player == player_turn:
                
                column = int(data)  
                print(column)
                if is_valid_move(column):#Checks for valid move
                    make_move(column, player)
                    if check_win(player):
                        make_move(column, player)
                        for client in clients:
                            client.sendall(pickle.dumps({'board':board,'wins': True,}))#Sends the updated board after the move is made
                        game_over = True
                        
                        print(f"Player {player + 1} wins!")#Sends the win message in case a player wins
                    else:
                        player_turn = 1 - player_turn  # Switch turns only if the game is not over
                        update_clients()
                    
                else:
                    # Send a message to the client indicating the move was invalid
                    client.sendall(pickle.dumps({'invalid_move': True}))

        except:
            break
    
    client.close()
    if(client in clients):
        clients.remove(client)


def is_valid_move(column):
    #checks if a move is valid
    return 0 <= column < 7 and board[0][column] == 0


def make_move(column, player):
    #updates the board based on the move made
    row = 5
    while board[row][column] != 0:
        row -= 1
    board[row][column] = player + 1


def check_win(player):
    # Check horizontal
    for i in range(6):
        for j in range(4):
            if board[i][j] == board[i][j+1] == board[i][j+2] == board[i][j+3] == player + 1:
                return True
    # Check vertical
    for i in range(3):
        for j in range(7):
            if board[i][j] == board[i+1][j] == board[i+2][j] == board[i+3][j] == player + 1:
                return True
    # Check diagonals
    for i in range(3):
        for j in range(4):
            if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == board[i+3][j+3] == player + 1:
                return True
    for i in range(3):
        for j in range(3, 7):
            if board[i][j] == board[i+1][j-1] == board[i+2][j-2] == board[i+3][j-3] == player + 1:
                return True
    return False

def update_clients():
    for client in clients:
        try:
            data_to_send = {
                'board': board,
                'player_turn': player_turn
            }
            serialized_data = pickle.dumps(data_to_send)
            client.sendall(serialized_data)
        except Exception as e:
            print(f"Error sending data to client: {e}")

def main():
    #SSL connection of the eserver
    
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTIFICATE_FILE, keyfile=KEY_FILE)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CONNECTIONS)
    print("Server listening...")
    #clients is a list which stores all the clients
    while len(clients) < MAX_CONNECTIONS:
        client, address = server.accept()
        print(client)
        ssl_connection = context.wrap_socket(client, server_side=True)
        
        clients.append(ssl_connection)
        
        

        player = len(clients) - 1
        print(f"Player {player + 1} connected.")
        #On successfull connection, sends the player data
        ssl_connection.sendall(bytes(str(player), 'utf-8'))
        wait_mess=ssl_connection.recv(2048).decode()
        print(wait_mess)
        #Waiting message in case only one player has joined(Has to wait for player 2)
        if(len(clients)<2):
        #True waiting message(The waiting message has to displayed)
            ssl_connection.sendall(bytes("TRUE",'utf-8'))
        if(len(clients)==2):
            for client in clients:
            #Both the players have joined. No waiting message display required Start the game
                client.sendall(bytes("FALSE",'utf-8'))
    
        threading.Thread(target=handle_client, args=(ssl_connection, player)).start()

        
    
if __name__ == "__main__":
    main()
