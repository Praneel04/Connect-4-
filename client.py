import socket
import pygame
import ssl  
import sys
import pickle
import numpy as np
# Constants
pygame.init()
HOST = '127.0.0.1'  # Localhost
PORT = 5559  # Port to connect to
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
current_player = 0
# Screen dimensions
player_turn=0
row_size=6
column_size=7
board=np.zeros((row_size,column_size))
font = pygame.font.Font(None, 36)  # Use default system font with size 36

size=100
height=int((row_size+1)*size)
width=int(column_size*size)
row_count=[0,0,0,0,0,0,0]
logged_in_users = []

# Initialize Pygame
def authenticate(username, password):
    with open('users.txt', 'r') as file:
        for line in file:
            stored_username=line.strip().split(',')[1]
            stored_password = line.strip().split(',')[2]
            if stored_username == username and stored_password == password:
                return True
    return False

screen_size=(width,height)
screen=pygame.display.set_mode(screen_size)
# def signup():
#     new_username = input("Enter the new username: ")
#     new_password = input("Enter the new password: ")

#     with open('users.txt', 'a') as file:
#         file.write(f"{new_username},{new_password}\n")

#     print("Signup successful. You can now login with your new credentials.")
def display_player_number(player_number):
    # Create a text surface with the player number
    text_surface = font.render(f"Player: {player_number + 1}", True, WHITE)
    
    # Get the bounding rectangle of the text surface
    text_rect = text_surface.get_rect()
    
    # Position the text at the top center of the screen
    text_rect.topleft = (0, 0)
    
    # Draw the text surface onto the screen
    screen.blit(text_surface, text_rect)
    
    # Update the display
    pygame.display.flip()
def display_waiting_message(message):
    # Clear the screen
    screen.fill(WHITE)
    
    # Create a text surface with the waiting message
    text_surface = font.render(message, True, BLACK)
    
    # Get the bounding rectangle of the text surface
    text_rect = text_surface.get_rect()
    
    # Center the text horizontally and vertically on the screen
    text_rect.center = (screen_width // 2, screen_height // 2)
    
    # Draw the text surface onto the screen
    screen.blit(text_surface, text_rect)
    
    # Update the display
    pygame.display.flip()
def draw_board():
    #To draw the initial board
    pygame.draw.rect(screen,BLUE,(0,size,width,(row_size*size)))
    for i in range(row_size):
        for j in  range(column_size):
            pygame.draw.circle(screen,BLACK,(int((j*size)+size/2),int(size+size/2+(i*size))),int(size/2-5))
    pygame.display.update()
def validity(col):
    #checks if a move is valid
    row=row_count[col]
    if(row<row_size):
        if(board[row][col]==0):
            return True
    return False
def update_board(new_board):
    #updates board list based on the parameter new_board
    global board
    
    
    for row in range(row_size):
        for col in range(column_size):
            
            
            if new_board[row][col] != board[row][col]:
                board[row][col] = new_board[row][col]
                
                if new_board[row][col] == 1:
                    pygame.draw.circle(screen, RED, (int(col * size + size / 2), int((5 - row_count[col]) * size + size + size / 2)), int(size / 2 - 5))
                else:
                    pygame.draw.circle(screen, YELLOW, (int(col * size + size / 2), int((5 - row_count[col]) * size + size + size / 2)), int(size / 2 - 5))
                row_count[col] += 1
    pygame.display.update()
def get_index_from_size(size):
    index=size//100
    return index
def display_win_message(message, duration):
    # Clear the screen
    screen.fill(WHITE)
    
    # Create a text surface with the win message
    text_surface = font.render(message, True, BLACK)
    
    # Get the bounding rectangle of the text surface
    text_rect = text_surface.get_rect()
    
    # Center the text horizontally and vertically on the screen
    text_rect.center = (screen_width // 2, screen_height // 2)
    
    # Draw the text surface onto the screen
    screen.blit(text_surface, text_rect)
    
    # Update the display
    pygame.display.flip()

    # Wait for the specified duration (in milliseconds)
    pygame.time.delay(duration)
def main():
    global board
    global player_turn
    print("Welcome to connect 4 game")
    running=True
    while running:
        #Authentication of the client
        print('''1.Login\n2.Signup''')
        ch=int(input("Enter your choice"))
        if ch == 1:
            username = input("Enter your username")
            password = input("Enter your password")
            if authenticate(username, password):
                #Authentication of the user
                print(logged_in_users)
                if username in logged_in_users:
                    print("You are already logged in as this user.")
                    continue  # Go back to the beginning of the loop to prompt for another choice
                else:
                    #SSL connection of the client to the server
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    context.check_hostname = False
                    context.load_verify_locations("localhost.crt")
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    ssl_socket = context.wrap_socket(client)
                    ssl_socket.connect((HOST, PORT))
                    print("Connected to server")
                    player_number = int(ssl_socket.recv(1024).decode())
                    print("You are player", player_number+1)
                    logged_in_users.append(username)
                    running = False
            else:
                print("Wrong username or password")
                sys.exit(0)
        elif(ch==2):
            #THis is for the signup feature. Adds the information of username and password to users.txt file
            name=input("Enter your name")
            username=input("Enter your username")
            password=input("Enter your password")
            with open('users.txt', 'a') as file:
                file.write(f"{name},{username},{password}\n")
            print("User registered successfully!")

    
    
    
    
    ssl_socket.sendall(bytes('Waiting message','utf-8'))
    wait='w'
    try:
        
        while wait:
            
            wait=ssl_socket.recv(1024).decode()
            
            while(wait=='TRUE'):
                display_waiting_message('Waiting for player 2')
                pygame.display.update()
                wait=ssl_socket.recv(1024).decode()
            if(wait=="FALSE"):
                break
    except:
        print("Could not get wait message")
    draw_board()

        
    running =True
    while running:
        display_player_number(player_number)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #If pygame quit is pressed
                ssl_socket.sendall(bytes('QUIT', 'utf-8'))
                running=False
                ssl_socket.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                #if the mouse is moved accross the screen, the ball has to move along with it
                
                pygame.draw.rect(screen, BLACK, (0, 0, width, size))
                posx = event.pos[0]
                if player_number == 0:
                    pygame.draw.circle(screen, RED, (posx, int(size / 2)), int(size / 2 - 5))
                else:
                    pygame.draw.circle(screen, YELLOW, (posx, int(size / 2)), int(size / 2 - 5))
                pygame.display.update()
                
            
            if player_number == player_turn:
                #Only runs if it is the right player's turn
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #When a square is clicked
                    x = get_index_from_size(event.pos[0]) 
                    print(x)
                    ssl_socket.sendall(bytes(str(x), 'utf-8'))
            
                    data = b""
                    data=ssl_socket.recv(2048)
                    game_data = pickle.loads(data)
                    if('wins' in game_data):
                        #If win is received from the server
                        print(game_data)
                        board1 = game_data['board']
                        print(board1)
                        
                        # update_board(board1)
                        # print("Player turn is: ",player_turn)
                        
                            
                        display_win_message(f"Player {player_turn+1} wins!!!!!",5000)
                        running=False  
                        
                        print(f"{player_turn+1} wins!!!!!")
                        
                    elif 'invalid_move' in game_data:
                        #If invalid move is received by the server
                        print("Invalid move. Please try again.")
                        pygame.display.update()
                    else:
                        print(game_data)
                        board1 = game_data['board']
                        print(board1)
                        player_turn = game_data['player_turn']
                        update_board(board1)
                        pygame.display.update()
            else:
                #Listening to connections even when it is not the players turn in case a win occurs. Also has to update the board even though its not the players turn.
                try:
                    
                    data = b""
                    data=ssl_socket.recv(2048)
                    game_data = pickle.loads(data)
                    #Recieves board data from the server
                    if('wins' in game_data):
                        #If the opposite player has won
                        print(game_data)
                        board1 = game_data['board']
                        
                        
                        update_board(board1)
                        print(f"Player {player_turn+1} wins!!!!!")
                        #Update the board and display the win message
                        
                        display_win_message(f"Player {(player_turn)+1} wins!!!!!",5000)
                        
                        running=False
                        
                    else:
                        #Updates the board
                        print(game_data)
                        board1 = game_data['board']
                        print(board1)
                        player_turn = game_data['player_turn']
                        update_board(board1)
                        
                        pygame.display.update()
                except socket.error as s:
                    print("Error occured",s)



if __name__ == "__main__":
    main()
