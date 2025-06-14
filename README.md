This is a collection of scripts that are useful when playing Wordle and the variant "Don't Wordle"

## Wordle

The Wordle helper is a simple assistant for the game of Wordle.
It won't tell you the correct answer so it does not constitute cheating :)
It merely tells you what possible words are left to guess after each of your guesses.
Please note that these words are not always the optimal choices to provide more clues.
I suggest that once the helper has narrowed the list of words down to a number you can manage,
you analyze the words to find out what word (with what key letters) will allow you to distinguish between them all.

Simply run `wordle_helper.py` with Python, no packages needed!
While playing Wordle fill in what you know about the word according to the prompts from the helper.


Happy wordling!

## Don't Wordle
The rules for "Don't Wordle" are at the top of `dont_wordle_solver.py`, which is actually a very limited algorithm and not a full solver

You will probably also find `advanced_word_finder.py` useful for this game.