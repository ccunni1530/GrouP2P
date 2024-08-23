import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "group2p"))
from group2p.group2p import *
from threading import Thread
from time import monotonic, sleep


class Game(object):
    _player1 = {"id": None, "choice": None}
    _player2 = {"id": None, "choice": None}
    _groupID = ""

    def __init__(self, args, gp2p: GrouP2P):
        if args.host:
            self._player1["id"] = gp2p.userID
            self._groupID = gp2p.create_group("GrouP2P Game").json()["response"]["id"]
        else:
            self._player2["id"] = gp2p.userID
            if not args.join: raise argparse.ArgumentError("You need to specify whether you are a host or a member!")
            if not args.sharetoken: raise argparse.ArgumentError("You must specify a share token for the group!")
            self._groupID = gp2p.join_group(args.join, args.sharetoken)["response"]["id"]
    
    @property
    def gid(self): return self._groupID

    @property
    def p1(self): return self._player1

    @property
    def p2(self): return self._player2

def process(data: str, game: Game):
    def play_game(x, y) -> int:
        mappings = {
            "rock": ["scissors", "rock", "paper"],
            "scissors": ["paper", "scissors", "rock"],
            "paper": ["rock", "paper", "scissors"]
        }
        return mappings[x].index(y)

    # Message format: [first 3 digits of gid][first 5 digits of user id][mapping key]
    win_messages = ["Player 1 wins!", "Tie!", "Player 2 wins!"]
    if data[:3] == game.gid[:3]:
        if data[3:8] == game.p1["id"][:5]:
            print("Detected your message.")
            game.p1["choice"] = data[8:]
        elif data[3:8] == game.p2["id"][:5]:
            print("Detected player 2's message.")
            game.p2["choice"] = data[8:]

        if game.p1["choice"] and game.p2["choice"]:
            result = play_game(game.p1["choice"], game.p2["choice"])
            print(win_messages[result])
            return result
        else:
            return -1
            

handle = None
initLoop = True

def listen(game: Game):
    global timer
    global handle
    global initLoop
    while initLoop or len(handle._msgHistory.keys()) > 0: #Loop forever as long as groups are there to listen to
        for group in handle._msgHistory.keys():
            newMsgList = handle.receive(group)
            if len(newMsgList) > 0: #If there are new messages present, add them
                for message in newMsgList:
                    created_at = message["created_at"]
                    text = message["text"]
                    process(text, game)
        
        timer = monotonic()
        sleep(0.01)
    print(f"Listener ended:\n\tMonitored groups (ID): {handle._msgHistory.keys()}")

def main():
    global handle
    global initLoop
    parser = argparse.ArgumentParser(prog="GrouP2P Example",
                                     usage="python3 example.py [-h] [-j]",
                                     description="A game of Rock Paper Scissors played over GroupMe servers.")
    parser.add_argument("-ht", "--host", action="store_true")
    parser.add_argument("-jn", "--join", action="store")
    parser.add_argument("-st", "--sharetoken", action="store")
    args = parser.parse_args()

    print("Creating handle...")
    handle = GrouP2P()
    print("Creating group...")
    response = handle.create_group()
    print("Converting response to JSON...")
    response = response.json()
    print(f"JSON response: {response}")
    t = Thread(target=listen, args=(Game(args, handle),))
    try:
        print("\n\n\nListening for messages...")
        t.run()
        if handle.send(".", response["response"]["id"]): initLoop = False
        while True: sleep(1)
    except KeyboardInterrupt:
        print(f"\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        t.join()
    finally:
        print("\nCleaning up group...")
        for group in handle._msgHistory.keys():
            code = handle.delete_group(group).status_code
            if code != 200: print(f"An error has occured deleting group {group} ({code}).")
        print("Finished cleanup.")

try:
    main()
finally:
    pass