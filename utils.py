import random


def shuffle(array):
    for i in range(len(array) - 1, 0, -1):
        j = random.randrange(i + 1)
        array[i], array[j] = array[j], array[i]
