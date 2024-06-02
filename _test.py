from game import Game

game = Game()

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