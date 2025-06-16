import sys
from tqdm import tqdm
import string
from collections import Counter

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

def get_user_input(prompt):
    """Get user input with prompt"""
    print(f"\n{prompt}")
    return sys.stdin.readline().strip()

def parse_position_constraints(input_str):
    """Parse position constraints like '0a+,1b-,4c+' into dict"""
    if not input_str:
        return {}
    
    constraints = {}
    try:
        parts = input_str.split(',')
        for part in parts:
            pos = int(part[0])
            letter = part[1]
            must_be = part[2] == '+'
            if pos not in constraints:
                constraints[pos] = []
            constraints[pos].append((letter, must_be))
    except (ValueError, IndexError):
        print("Invalid format. Use format like: 0a+,1b-,4c+ (position+letter+/- for must/must not be)")
        return {}
    
    return constraints

def get_wordle_feedback(guess, target):
    """Get exact Wordle feedback pattern (g=green, y=yellow, b=grey)"""
    if len(guess) != 5 or len(target) != 5:
        raise ValueError("Words must be 5 letters")
    
    feedback = ['b'] * 5  # Start with all grey
    target_counts = Counter(target)
    
    # First pass: mark greens and reduce target counts
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = 'g'
            target_counts[guess[i]] -= 1
    
    # Second pass: mark yellows where letters remain
    for i in range(5):
        if feedback[i] == 'b' and target_counts[guess[i]] > 0:
            feedback[i] = 'y'
            target_counts[guess[i]] -= 1
    
    return ''.join(feedback)

def satisfies_constraints(word, greens, yellow_letters, yellow_positions, greys):
    """Check if word satisfies all Don't Wordle constraints"""
    # Check green constraints
    for pos, letter in greens.items():
        if word[pos] != letter:
            return False
    
    # Check yellow constraints - must contain all yellow letters
    for letter in yellow_letters:
        if letter not in word:
            return False
    
    # Check yellow position constraints - yellow letters can't be in forbidden positions
    for pos, letter in yellow_positions:
        if word[pos] == letter:
            return False
    
    # Check grey constraints - can't contain grey letters unless required by green/yellow
    required_letters = set(greens.values()) | yellow_letters
    for letter in greys:
        if letter not in required_letters and letter in word:
            return False
    
    return True

def filter_valid_words(words, greens, yellow_letters, yellow_positions, greys):
    """Filter words that satisfy current constraints"""
    return [word for word in words if satisfies_constraints(word, greens, yellow_letters, yellow_positions, greys)]

def filter_by_letter_counts(words, letter_counts):
    """Filter words by exact letter count requirements"""
    if not letter_counts:
        return words
    
    filtered = []
    for word in words:
        word_counter = Counter(word)
        matches = True
        for letter, count in letter_counts.items():
            if word_counter[letter] != count:
                matches = False
                break
        if matches:
            filtered.append(word)
    return filtered

def filter_by_min_letter_counts(words, min_counts):
    """Filter words by minimum letter count requirements"""
    if not min_counts:
        return words
    
    filtered = []
    for word in words:
        word_counter = Counter(word)
        matches = True
        for letter, min_count in min_counts.items():
            if word_counter[letter] < min_count:
                matches = False
                break
        if matches:
            filtered.append(word)
    return filtered

def parse_letter_counts(input_str):
    """Parse letter count input like 'a2,b1,c3' into dict"""
    if not input_str:
        return {}
    
    counts = {}
    try:
        pairs = input_str.split(',')
        for pair in pairs:
            letter = pair[0]
            count = int(pair[1:])
            counts[letter] = count
    except (ValueError, IndexError):
        print("Invalid format. Use format like: a2,b1,c3")
        return {}
    
    return counts

def count_survivors(guess, answer, valid_words):
    """Count how many words would remain valid after this guess"""
    target_feedback = get_wordle_feedback(guess, answer)
    survivors = 0
    
    for word in valid_words:
        if get_wordle_feedback(guess, word) == target_feedback:
            survivors += 1
    
    return survivors

def main():
    # Load word lists
    print("Loading word lists...")
    answers = read_file("wordle-answers-alphabetical.txt")
    allowed = read_file("wordle-allowed-guesses.txt")
    all_words = answers + allowed
    
    print(f"Loaded {len(all_words)} possible words")
    
    # Get the true answer word
    answer = get_user_input("Enter the true answer word (5 letters):").lower()
    if len(answer) != 5:
        print("Answer must be exactly 5 letters!")
        return
    if answer not in all_words:
        print(f"Warning: '{answer}' not found in word lists!")
    
    # Get position constraints (greens and yellows)
    print("\nPosition constraints format: '0a+,1b-,4c+' where:")
    print("  + means GREEN (letter must be at that position)")
    print("  - means YELLOW (letter must be in word but NOT at that position)")
    position_input = get_user_input("Position constraints:")
    position_constraints = parse_position_constraints(position_input)
    
    # Parse constraints
    greens = {}
    yellow_letters = set()
    yellow_positions = set()
    
    for pos, constraint_list in position_constraints.items():
        for letter, must_be in constraint_list:
            if must_be:  # Green constraint
                greens[pos] = letter
                print(f"Green: {letter} at position {pos}")
            else:  # Yellow constraint
                yellow_letters.add(letter)
                yellow_positions.add((pos, letter))
                print(f"Yellow: {letter} not at position {pos}")
    
    # Get grey letters
    grey_input = get_user_input("Grey letters (just the letters, e.g. 'abc'):").lower()
    greys = set(letter for letter in grey_input if letter.isalpha())
    if greys:
        print(f"Grey letters: {sorted(greys)}")
    
    # Get exact letter count constraints
    exact_counts_input = get_user_input("Exact letter counts (e.g. 'a2,b1' for exactly 2 a's and 1 b):")
    exact_counts = parse_letter_counts(exact_counts_input.lower())
    if exact_counts:
        print(f"Exact counts: {exact_counts}")
    
    # Get minimum letter count constraints  
    min_counts_input = get_user_input("Minimum letter counts (e.g. 'a2,b1' for at least 2 a's and 1 b):")
    min_counts = parse_letter_counts(min_counts_input.lower())
    if min_counts:
        print(f"Minimum counts: {min_counts}")
    
    # Filter to get current valid words
    print("\nFiltering valid words...")
    valid_words = filter_valid_words(all_words, greens, yellow_letters, yellow_positions, greys)
    print(f"After basic constraints: {len(valid_words)}")
    
    # Apply letter count constraints
    if exact_counts:
        valid_words = filter_by_letter_counts(valid_words, exact_counts)
        print(f"After exact count constraints: {len(valid_words)}")
    
    if min_counts:
        valid_words = filter_by_min_letter_counts(valid_words, min_counts)
        print(f"After minimum count constraints: {len(valid_words)}")
    
    print(f"Final valid words: {len(valid_words)}")
    
    if len(valid_words) == 0:
        print("No valid words remaining!")
        return
    
    if len(valid_words) <= 10:
        print(f"Remaining words: {valid_words}")
    
    # Calculate survivors for each possible guess
    print(f"\nAnalyzing {len(valid_words)} possible guesses...")
    guess_scores = []
    
    for guess in tqdm(valid_words, desc="Calculating survivors"):
        survivors = count_survivors(guess, answer, valid_words)
        letters_used = set(guess) | set(yellow_letters) | set(greys) | set(greens.values())
        unused_letters_count = 26 - len(letters_used)
        guess_scores.append((guess, survivors, unused_letters_count, survivors * unused_letters_count))
    
    # Sort by survivors (descending - more survivors is better for Don't Wordle)
    guess_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Display results
    print(f"\nTOP 30 GUESSES (sorted by remaining words):")
    print("Word\t\tRemaining Words\t\tUnused Letters\t\tFinal Don't Wordle Score")
    print("-" * 60)
    
    for word, survivors, unused_letters_count, score in guess_scores[:30]:
        print(f"{word}\t\t{survivors}\t\t\t{unused_letters_count}\t\t\t{score}")
    
    # Show some stats
    if guess_scores:
        best_word, min_survivors, min_unused_letters_count, min_score = guess_scores[-1]
        worst_word, max_survivors, max_unused_letters_count, max_score = guess_scores[0]
        print(f"\nBest guess: {best_word} (leaves {min_survivors} words, {min_unused_letters_count} unused letters, {min_score} score)")
        print(f"Worst guess: {worst_word} (leaves {max_survivors} words, {max_unused_letters_count} unused letters, {max_score} score)")

if __name__ == "__main__":
    main() 