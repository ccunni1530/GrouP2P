import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "group2p"))
from group2p.group2p import *
from threading import Thread
from time import monotonic, sleep

handle = None
initLoop = True

def listen():
    global timer
    global handle
    global initLoop
    while initLoop or len(handle._msgHistory.keys()) > 0: #Loop forever as long as groups are there to listen to
        for group in handle._msgHistory.keys():
            newMsgList = handle.receive(group)
            if len(newMsgList) > 0: #If there are new messages present, add them
                for message in newMsgList:
                    created_at = message["created_at"]
                    name = message["name"]
                    text = message["text"]
                    print(f"[{created_at}] From {name}: {text}\n--")
                newMsgList + handle._msgHistory[group]
                handle._msgHistory[group] = newMsgList
        
        timer = monotonic()
        sleep(0.01)
    print(f"Listener ended:\n\tMonitored groups (ID): {handle._msgHistory.keys()}")

def main():
    global handle
    global initLoop
    parser = argparse.ArgumentParser(prog="GrouP2P Example", 
                                    description="A simple demonstration of the capabilities of the GrouP2P module.")
    parser.add_argument("-c", "--cleanup", action="store_true", help="delete created group(s) after program ends.")
    parser.add_argument("-s", "--savetoken", action="store_true", help="saves the token to config.json")
    parser.add_argument("-r", "--removetoken", action="store_true", help="removes the token from config.json and sets it to null.")
    parser.add_argument("-t", "--token", action="store", default="", help="specify the token to be used to connect to the GroupMe API.")
    args = parser.parse_args()

    print("Creating handle...")
    handle = GrouP2P(args.token)
    print("Creating group...")
    response = handle.create_group()
    print("Converting response to JSON...")
    response = response.json()
    print(f"JSON response: {response}")
    t = Thread(target=listen)
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
        if args.cleanup:
            print("\nCleaning up group(s)...")
            for group in handle._msgHistory.keys():
                code = handle.delete_group(group).status_code
                if code != 200: print(f"An error has occured deleting group {group} ({code}).")
            print("Finished cleanup.")
        if args.removetoken:
            handle.set_config("token", None)
        if args.savetoken:
            handle.set_config("token", handle._user["connection"]._token)

try:
    main()
finally:
    pass