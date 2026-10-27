import argparse
import logging
import os
import signal
from time import sleep

running = True  # Runs the main loop


def interrupt_sig_handler(signum, frame):
    """
    So handlers can process signals as I need or want
    """
    global running
    running = False
    ...


# binding my function to the signal SIGINT
signal.signal(signal.SIGINT, interrupt_sig_handler)

# Main Loop
while running:
    # Things that my daemon has to do is in here. Like responding with a TUI if CLI call the daemon. Respond with a tool orquestrator and the response of each tool if the user select some option in the TUI and etc.
    print("Hey")
    sleep(1)
    if not running:
        print("Safy closing...")
        sleep(10)

# If I understand correct this is a very simple daemon skeleton.
