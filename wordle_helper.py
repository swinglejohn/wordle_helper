import sys
import numpy as np
import random

def process_input(input):
    for i in range(len(input)):
        input[i] = input[i][:-1] # cuts off newline character
    return input

def read_file(filename):
    with open(filename) as f:
        content = f.readlines()
    return process_input(content)

def process_words(words, positions, unused, wrong_spots):
    new_words = []
    for word in words:
        skip = False
        for i, c in enumerate(positions):
            if c != '.' and word[i] != c:
                skip = True
                break
        if skip: continue
        for c in word:
            if c in unused:
                skip = True
                break
        if skip: continue
        for c in wrong_spots:
            skip = c not in word
            for i in wrong_spots[c]:
                if word[i-1] == c:
                    skip = True
            if skip: break
        if skip: continue
        new_words.append(word)
    return new_words

answers = read_file("wordle-answers-alphabetical.txt")
allowed = read_file("wordle-allowed-guesses.txt")
print(len(answers))
print(len(allowed))
answers.extend(allowed)
words = answers
random.shuffle(words)
print("CTRL c should abort this program for you")
print("There are " + str(len(words)) + " possible words to choose from at the beginning of a game of wordle (total word list)")
print("Good Luck!")


positions = ['.' for i in range(5)]
unused = set()
while len(words) > 1:
    print("\nEnter what positions (green squares) you know with unkown positions marked as a period")
    print("Example: input of 'app..' could be 'apple'")
    print("You must enter exactly 5 characters")
    known = sys.stdin.readline().strip()
    for i, c in enumerate(known, 0):
        if c != '.':
            positions[i] = c

    print("\nNow enter all of the new characters you ruled out (white or black squares) since the last run")
    print("(You don't have to re-enter things from earlier)")
    print("just enter them all together in one line with no spaces between")
    print("Example: gruea")
    grey = sys.stdin.readline().strip()
    for c in grey:
        unused.add(c)
    
    wrong_spots = dict()
    print("\nType the letters that are in the wrong position (yellow squares)")
    print("You have to re-type any from before")
    print("First put just the number of letters you are going to put")
    print("Then put each letter on a separate line")
    print("Precede each letter with the numbers of the positions it can not occupy")
    print("Numbers from 1 to 5. No spaces.")
    print("Example:\n2\n13a\n43x\n")
    num_yellow = int(sys.stdin.readline().strip())
    for i in range(num_yellow):
        yellow = (sys.stdin.readline().strip())
        yellow = [c for c in yellow]
        wrong_spots[yellow[-1]] = [int(c) for c in yellow[:-1]]
    
    print("\nerror checking:")
    print(positions)
    print(unused)
    print(wrong_spots)

    # Finally the actual problem solving!
    words = process_words(words, positions, unused, wrong_spots)
    print("There are only " + str(len(words)) + " possible words left!")
    print("The first 10 are:")
    print(words[:10])



