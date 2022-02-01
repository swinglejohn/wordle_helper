import sys
import random

def process_input(input):
    for i in range(len(input)-1): # -1 because the last character doesn't have a \n
        input[i] = input[i][:-1] # cuts off newline character
    return input

def read_file(filename):
    with open(filename) as f:
        content = f.readlines()
    return process_input(content)

def process_words(words, letters):
    new_words = []
    for word in words:
        skip = False
        for c in letters:
            if c not in word:
                skip = True
                break
        if not skip: new_words.append(word)
    return new_words

def word_with(m):
    letters = set()
    if not m: print("\nEnter the letters you want your word to contain")
    if not m: print("Just enter them all together in one line with no spaces between.")
    if not m: print("Example: fml")
    raw = sys.stdin.readline().strip()
    for c in raw:
        letters.add(c)
    print("Letters to include: " + str(letters))
    return letters


# read in the wordlists
answers = read_file("wordle-answers-alphabetical.txt")
allowed = read_file("wordle-allowed-guesses.txt")
#print(len(answers))
#print(len(allowed))
answers.extend(allowed)
words = answers
random.shuffle(words)

print("CTRL c should abort this program for you")
while True:
    letters = word_with(False)
    matching_words = process_words(words, letters)
    print("There are " + str(len(matching_words)) + " that contain those letters!")
    print(matching_words)


