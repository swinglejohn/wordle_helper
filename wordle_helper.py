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

def play_round(positions, unused, m):

    if not m: print("\nEnter what positions (green squares) you know with unkown positions marked as a period")
    if not m: print("Example: input of 'app..' could be 'apple'")
    if not m: print("You must enter exactly 5 characters.")
    if m: print("positions (greens):")
    known = sys.stdin.readline().strip()
    for i, c in enumerate(known, 0):
        if c != '.':
            positions[i] = c
    
    wrong_spots = dict()
    if not m: print("\nType the letters that are in the wrong position (yellow squares).")
    if not m: print("You have to re-type any from before.")
    if not m: print("First put just the number of letters you are going to put.")
    if not m: print("Then put each letter on a separate line. If none be sure to put 0.")
    if not m: print("Precede each letter with the numbers of the positions it can not occupy.")
    if not m: print("Numbers from 1 to 5. No spaces.")
    if not m: print("Example:\n2\n13a\n43x\n")
    if m: print("wrong spots (yellow):")
    num_yellow = int(sys.stdin.readline().strip())
    for i in range(num_yellow):
        yellow = (sys.stdin.readline().strip())
        yellow = [c for c in yellow]
        wrong_spots[yellow[-1]] = [int(c) for c in yellow[:-1]]

    if not m: print("\nNow enter all of the new characters you ruled out (white or black squares) since the last run.")
    if not m: print("(You don't have to re-enter things from earlier)")
    if not m: print("Just enter them all together in one line with no spaces between.")
    if not m: print("Example: gruea")
    if m: print("new ruled out characters (white, grey, or black):")
    grey = sys.stdin.readline().strip()
    for c in grey:
        # This conditional protects from duplicate letter issues
        if c not in wrong_spots and c not in positions:
            unused.add(c)
    
    print("\nerror checking:")
    print("Green Postions: " + str(positions))
    print("Completely Unused Letters: " + str(unused))
    print("Letters that are in the word and the positions they can not be in:\n" + str(wrong_spots) + "\n")
    return wrong_spots

def is_end(words):
    if len(words) == 1:
        print("Congratulations! It looks like you won!")
        return True
    if len(words) < 1:
        print("Uh oh, looks like maybe you input something wrong?")
        print("Try running the program again")
        print("If you think it's a bug, let John know!")
        return True
    return False



# read in the wordlists
answers = read_file("wordle-answers-alphabetical.txt")
print(answers[:5] + answers[-5:])
allowed = read_file("wordle-allowed-guesses.txt")
print(allowed[:5] + allowed[-5:])
#print(len(answers))
#print(len(allowed))
answers.extend(allowed)
words = answers
random.shuffle(words)


print("CTRL c should abort this program for you")
print("There are " + str(len(words)) + " possible words to choose from at the beginning of a game of wordle (total word list)")

print("For the minimalistic menu enter 'y' or 'Y'")
print("Otherwise anything else will suffice")
minimal = sys.stdin.readline().strip()
m = (minimal.lower() == 'y')
print("Good Luck!\n")


positions = ['.' for i in range(5)]
unused = set()
for i in range(1, 6):
    if is_end(words):
        break
    print("After guess " + str(i))
    wrong_spots = play_round(positions, unused, m)
    words = process_words(words, positions, unused, wrong_spots)
    print("Note: The optimal next guess may not be one of the remaining possible words")
    print("There are only " + str(len(words)) + " possible words left!")
    n_show = 25
    print("The first " + str(min(n_show, len(words))) + " are:")
    print(words[:n_show], end="\n\n")


