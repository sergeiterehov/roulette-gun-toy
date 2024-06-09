import os
from game import Game

def handle_tell():
  os.system('clear')
  print(" ".join([m.text for m in game.message]))
  game.print_state()

game = Game()

game.on_tell = handle_tell

game.reset()
game.begin()

while True:
  x = input("COMMAND:")

  if x == "s":
    game.shut()
  elif x == "r":
    game.reload()
  elif x == "o":
    game.ok()
  elif x == "+":
    game.set_direction(True)
  elif x == "-":
    game.set_direction(False)