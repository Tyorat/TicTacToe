# TicTacToe
Tic -Tac-Toe game with server which connect two users for play( use only built-in modules)
**********************************************
#Server part
Server part don't need any install (only python>=3.8).
When you run it you must lock port and ip. For know for address socket.
Start file in src(source directory) in server_code file main.py
After run  he handles all request, when user want to start game server put in him in a wait queue. After that he wait 
for another player. When server found two players or more, he connects two players in one game.
After that he send one of him(randomly) that he can make a turn, and hi make a turn. 
And so they take turns making moves until the end of the match, after which they can start another game.
****************************************************
#Client part
Need install pyqt5 for work gui. Run file is client.py
Client part connect to server(need username and password),
after that he got token.Token need for take turn and find game. 
****************************************************
#Example run
* Server:
python3 main.py 8080
(8080 is server port)
* Client:
python3 client.py 192.168.17.32 8080
  (192.168.17.32 is ip server)
  
***************************************************
#Issues and feature to do
* GUI use sync interface, so he blocks update window. So before he doesn't get answer from server he cann't display
turn of player and doesn't block button( if he clicks too much, he will make a move to the front).
  
* Also while user waiting for opponent or turn opponent, game must show something.
* Add test and make more try exception
* Add AI(hard, easy, medium)
* Add some sound