import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import main

print("main.py imported and loaded successfully!")
pygame.quit()
