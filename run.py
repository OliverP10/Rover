import logging
from Rover import Rover


logging.basicConfig(filename='Rover.log',
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
            )

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))

logging.getLogger().addHandler(streamHandler)

rover: Rover = Rover()
