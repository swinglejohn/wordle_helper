import sys
import random
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

def filter_by_required_letters(words, required_letters):
    """Filter words that must contain all specified letters"""
    if not required_letters:
        return words
    
    filtered = []
    for word in words:
        if all(letter in word for letter in required_letters):
            filtered.append(word)
    return filtered

def filter_by_banned_letters(words, banned_letters):
    """Filter out words containing any banned letters"""
    if not banned_letters:
        return words
    
    filtered = []
    for word in words:
        if not any(letter in word for letter in banned_letters):
            filtered.append(word)
    return filtered

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

def filter_by_position_constraints(words, position_constraints):
    """Filter by letters that must/must not be in specific positions"""
    if not position_constraints:
        return words
    
    filtered = []
    for word in words:
        matches = True
        for pos, (letter, must_be) in position_constraints.items():
            if must_be and word[pos] != letter:
                matches = False
                break
            elif not must_be and word[pos] == letter:
                matches = False
                break
        if matches:
            filtered.append(word)
    return filtered

def get_user_input(prompt, allow_empty=True):
    """Get user input with prompt"""
    print(f"\n{prompt}")
    response = sys.stdin.readline().strip()
    return response if response or allow_empty else None

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
            constraints[pos] = (letter, must_be)
    except (ValueError, IndexError):
        print("Invalid format. Use format like: 0a+,1b-,4c+ (position+letter+/- for must/must not be)")
        return {}
    
    return constraints

def main():
    # Load word lists
    print("Loading word lists...")
    answers = read_file("wordle-answers-alphabetical.txt")
    allowed = read_file("wordle-allowed-guesses.txt")
    answers.extend(allowed)
    words = answers
    random.shuffle(words)
    
    print(f"Loaded {len(words)} words total")
    print("CTRL+C to exit\n")
    
    while True:
        print("=" * 50)
        print("ADVANCED WORD FINDER")
        print("=" * 50)
        
        # Get filtering criteria
        required = get_user_input("Letters that MUST be in the word (e.g., 'abc'):")
        required_set = set(required) if required else set()
        
        banned = get_user_input("Letters that must NOT be in the word (e.g., 'xyz'):")
        banned_set = set(banned) if banned else set()
        
        exact_counts = get_user_input("Exact letter counts (e.g., 'a2,b1' for exactly 2 a's and 1 b):")
        exact_counts_dict = parse_letter_counts(exact_counts)
        
        min_counts = get_user_input("Minimum letter counts (e.g., 'a2,b1' for at least 2 a's and 1 b):")
        min_counts_dict = parse_letter_counts(min_counts)
        
        positions = get_user_input("Position constraints (e.g., '0a+,1b-' for 'a' at pos 0, 'b' NOT at pos 1):")
        position_dict = parse_position_constraints(positions)
        
        # Apply filters
        filtered_words = words
        
        if required_set:
            filtered_words = filter_by_required_letters(filtered_words, required_set)
            print(f"After requiring letters {required_set}: {len(filtered_words)} words")
        
        if banned_set:
            filtered_words = filter_by_banned_letters(filtered_words, banned_set)
            print(f"After banning letters {banned_set}: {len(filtered_words)} words")
        
        if exact_counts_dict:
            filtered_words = filter_by_letter_counts(filtered_words, exact_counts_dict)
            print(f"After exact count constraints: {len(filtered_words)} words")
        
        if min_counts_dict:
            filtered_words = filter_by_min_letter_counts(filtered_words, min_counts_dict)
            print(f"After minimum count constraints: {len(filtered_words)} words")
        
        if position_dict:
            filtered_words = filter_by_position_constraints(filtered_words, position_dict)
            print(f"After position constraints: {len(filtered_words)} words")
        
        print(f"\nFINAL RESULT: {len(filtered_words)} matching words")
        
        if len(filtered_words) <= 50:
            print("\nMatching words:")
            for word in filtered_words:
                print(word)
        else:
            print(f"\nToo many words to display. First 20:")
            for word in filtered_words[:20]:
                print(word)
            print("...")

if __name__ == "__main__":
    main() 