import sys
from tqdm import tqdm


"""
This is a partial greedy solver for the game "Don't Wordle".
Here's the rule description:

HOW TO PLAY
Don't Wordle is just like Wordle but the opposite.

In Wordle, the goal is to guess a particular 5 letter word in 6 or fewer tries. In Don't Wordle, the goal is to NOT guess the word.

The catch is that your word attempts must respect the information you have learned in previous guesses.

🟩 - Once you place a letter correctly, then future guesses must contain that same letter in the same position
🟨 - Once you place a correct letter in an incorrect location, then future guesses must contain that letter in a different location
⬜ - Once letters have been guessed and eliminated, then you can no longer use them
The number of valid words remaining appears at the top, and it will shrink with each guess. If the number gets too low, you can use one of your "UNDOs" to reverse course.

Be careful! If you accidentally enter the Wordle word, the game is over even if you have some UNDOs remaining.
"""

"""
IMPORTANT - Algorithm limitations

- It only goes one layer deep (greedy)
- It assumes every letter in a guess is a miss (grey) and ignores the possibility of yellows and greens
    - This is a big limitation but it's still a fun tool
"""


def process_input(input_lines):
    """Remove newline characters from file input"""
    for i in range(len(input_lines)-1):
        input_lines[i] = input_lines[i][:-1]
    return input_lines

def read_file(filename):
    """Read word list from file"""
    with open(filename) as f:
        content = f.readlines()
    return process_input(content)

class DontWordleState:
    def __init__(self):
        # Green letters: position -> letter
        self.green_letters = {}
        # Yellow letters: set of (letter, position) pairs where letter can't be
        self.yellow_constraints = set()
        # Yellow letters that must be included somewhere
        self.yellow_letters = set()
        # Gray letters that are completely eliminated
        self.gray_letters = set()
        
    def add_green(self, position, letter):
        """Add a green letter constraint"""
        self.green_letters[position] = letter
        
    def add_yellow(self, letter, wrong_position):
        """Add a yellow letter constraint"""
        self.yellow_letters.add(letter)
        self.yellow_constraints.add((letter, wrong_position))
        
    def add_gray(self, letter):
        """Add a gray letter constraint"""
        self.gray_letters.add(letter)
        
    def is_valid_word(self, word):
        """Check if a word satisfies all current constraints"""
        # Check green constraints
        for pos, letter in self.green_letters.items():
            if word[pos] != letter:
                return False
                
        # Check yellow constraints - must contain all yellow letters
        for letter in self.yellow_letters:
            if letter not in word:
                return False
                
        # Check yellow position constraints - yellow letters can't be in wrong positions
        for letter, wrong_pos in self.yellow_constraints:
            if word[wrong_pos] == letter:
                return False
                
        # Check gray constraints - can't contain gray letters except in green positions or if needed for yellow
        for letter in self.gray_letters:

            # Note this isn't perfect. 
            # We should really check that there are no more than x number of the yellow letters where x is how many of the yellow letters are in the word.
            # And the same goes for green.

            # The user can make up for this by entering a yellow constraint for the gray position of a letter that also has a yellow
            # (so it has multiple yellow constraints)
            
            # Check if letter appears in any non-green position or is yellow
            green_positions = {pos for pos, green_letter in self.green_letters.items() if green_letter == letter}
            for pos, word_letter in enumerate(word):
                if word_letter == letter and pos not in green_positions and letter not in self.yellow_letters:
                    return False
                
        return True

def filter_valid_words(words, state):
    """Filter words that satisfy current game state"""
    return [word for word in words if state.is_valid_word(word)]

def find_best_guesses(valid_words, state, num_top=20):
    """Find the best guesses that minimize remaining words"""
    guess_scores = []
    
    print(f"Analyzing {len(valid_words)} possible guesses...")
    
    greens = state.green_letters.values()
    yellows = state.yellow_letters
    for guess in tqdm(valid_words, desc="Analyzing guesses"):
        total_remaining = 0
        
        # For each possible target word, see how many would remain after this guess
        # we break it into two cases because the green letters check is needed for correctness
        # but it's not needed on the first pass which is the slowest
        if greens or yellows:
            for target in valid_words:
                valid = True
                for c in (c for c in guess if c not in greens and c not in yellows):
                    if c in target:
                        valid = False
                        break
                total_remaining += valid
        else:
            for target in valid_words:
                valid = True
                for c in guess:
                    if c in target:
                        valid = False
                        break
                total_remaining += valid
        guess_scores.append((guess, total_remaining))
    
    # Sort by remaining words (descending - more is better)
    guess_scores.sort(key=lambda x: x[1], reverse=True)
    
    return guess_scores[:num_top]

def get_user_input(prompt):
    """Get user input with prompt"""
    print(f"\n{prompt}")
    return sys.stdin.readline().strip()

def parse_constraints(constraint_str):
    """Parse constraint string like 'g0a,y1b,x2c' into constraints"""
    if not constraint_str:
        return []
        
    constraints = []
    parts = constraint_str.split(',')
    
    for part in parts:
        if len(part) < 3:
            continue
        constraint_type = part[0].lower()
        position = int(part[1])
        letter = part[2].lower()
        constraints.append((constraint_type, position, letter))
        
    return constraints

def main():
    # Load word lists
    print("Loading word lists...")
    answers = read_file("wordle-answers-alphabetical.txt")
    allowed = read_file("wordle-allowed-guesses.txt")
    
    # All possible guesses (answers + allowed)
    all_words = answers + allowed
    valid_guesses = all_words
    
    print(f"Loaded {len(all_words)} possible words")
    
    state = DontWordleState()
    
    while True:
        print("\n" + "="*60)
        print("DON'T WORDLE SOLVER")
        print("="*60)
        
        print(f"Current valid words: {len(valid_guesses)}")
        
        if len(valid_guesses) <= 10:
            print(f"Remaining words: {valid_guesses}")
            
        # Get new constraints from user
        print("\nEnter new constraints from your last guess:")
        print("Green/Yellow format: g0a,y1b (g=green, y=yellow, position, letter)")
        print("Example: g0s,y1a")
        print("Leave empty if no green/yellow constraints:")
        
        constraint_input = get_user_input("Green/Yellow constraints:")
        
        if constraint_input:
            constraints = parse_constraints(constraint_input)
            for constraint_type, position, letter in constraints:
                if constraint_type == 'g':
                    state.add_green(position, letter)
                    print(f"Added green: {letter} at position {position}")
                elif constraint_type == 'y':
                    state.add_yellow(letter, position)
                    print(f"Added yellow: {letter} not at position {position}")
        
        # Get gray letters separately
        print("\nEnter gray letters (just the letters, no position needed):")
        print("Example if a, b, c are gray: abc")
        print("Leave empty if no gray letters:")
        
        gray_input = get_user_input("Gray letters:")
        
        if gray_input:
            for letter in gray_input.lower():
                if letter.isalpha():
                    state.add_gray(letter)
                    print(f"Added gray: {letter}")
        
        # Filter current valid words and guesses
        valid_guesses = filter_valid_words(valid_guesses, state)
        
        # Find best guesses
        if len(valid_guesses) == 0:
            print("No valid guesses remaining!")
            break
            
        if len(valid_guesses) <= 1:
            print("Game should be over - only 1 or fewer target words remain!")
            break
        
        print(f"Number of valid guesses: {len(valid_guesses)}")
            
        print("\nFinding best guesses...")
        best_guesses = find_best_guesses(valid_guesses, state, 30)
        
        print(f"\nTOP {len(best_guesses)} BEST GUESSES:")
        print("Word\t\tSimple Remaining Words Estimate")
        print("-" * 30)
        
        for word, avg_remaining in best_guesses:
            print(f"{word}\t\t{avg_remaining:.1f}")

if __name__ == "__main__":
    main() 