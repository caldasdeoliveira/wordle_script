# !ls

# # Main function

# +
# %%writefile agent.py
import os
import string
import pandas as pd
from typing import List
from collections import Counter

class Agent:
    def __init__(self, filename: str = "5LetterWords.txt",):
        self.filename = filename
        self.word_bag = self.initialize_words(self.filename)
        self.reset()
        
    def reset(self,):
        self.words = self.word_bag
        
    def initialize_words(self, filename: str,):
        assert os.path.exists(filename), f"File {filename} does not exist"
        
        with open(filename) as file:
            lines = {line.rstrip() for line in file}
        return lines
    
    def manual_game(self,):
        self.reset()
        for i in range(6):
            guess = self.get_guess()
            print(guess)
            result = input("What was the result? (0: wrong, 1: correct letter wrong place, 2: correct letter correct place)")
            result = [int(r) for r in result]
            if result == [2,2,2,2,2] or not result:
                print("Congrats!!")
                self.reset()
                return
            self.handle_result(guess, result)
        print("Sorry I failed you master!")
        self.reset()
        
    def handle_result(self, guess: str, result: List[int],):
        assert len(result) == 5, "Results must have length 5"
        assert len(guess) == 5, "Guess must have length 5"
        assert set(result) <= {0,1,2}, "Invalid values in result"
        
        seen_letters = dict.fromkeys(guess,0)
        for i,r in enumerate(result):
            if r == 0:
               self.remove_words_with_letter(letter = guess[i], previous_occurrences = seen_letters[guess[i]])
            elif r == 1:
                self.remove_words_correct_letter_in_wrong_spot(letter = guess[i], loc=i)
            elif r == 2:
                self.remove_words_correct_letter_in_correct_spot(letter = guess[i], loc=i)
            else:
                raise  ValueError("Result had unknown value that eluded the assert")
            seen_letters[guess[i]]+=1
    
    def remove_word_from_words(self, word: str,): #might be unnecessary
        self.words.remove(word)
    
    def remove_words_with_letter(self, letter: str, previous_occurrences: int = 0):
        if previous_occurrences > 0:
            self.words = {w for w in self.words if Counter(w)[letter] == previous_occurrences}
        else:
            self.words = {w for w in self.words if letter not in w}
    
    def remove_words_correct_letter_in_wrong_spot(self, letter: str, loc: int,):
        """
        Needs renaming for correct letters in wrong spot
        """
        assert loc >= 0 and loc <= 4, f"Letter location must be between 0 and 4, passed {loc}"
        self.words = {w for w in self.words if letter != w[loc] and letter in w}
        
    def remove_words_correct_letter_in_correct_spot(self, letter: str, loc: int,):
        """
        Needs renaming for correct letters in correct spot
        """
        assert loc >= 0 and loc <= 4, f"Letter location must be between 0 and 4, passed {loc}"
        self.words = {w for w in self.words if letter == w[loc]}
    
    def get_guess(self,):  
        assert self.words, "Word list is empty"
        
        df = pd.DataFrame([list(l) for l in self.words])
        scores_df = df.apply(pd.Series.value_counts)
        
        word_scores = dict.fromkeys(self.words,0) #{w: 0 for w in self.words}
        for word in word_scores:
            seen_letters = []
            for i,w in enumerate(word):
                if w not in seen_letters:
                    word_scores[word] += scores_df.loc[w,:].sum()
                    seen_letters.append(w) 
                word_scores[word] += scores_df.loc[w,i]*0.5
        return max(word_scores, key=word_scores.get)
    
if __name__ == "__main__":
    agent = Agent()
    agent.manual_game()
# -

from agent import Agent

a = Agent()

a.manual_game()

# # Testing

# +
# %%writefile test.py
import os
import string
import pandas as pd
from typing import List, Type
from agent import Agent
import random

from ipywidgets import IntProgress
from IPython.display import display

class Tester:
    def __init__(self, agent: Type[Agent], filename: str = "5LetterWords.txt"):
        self.filename = filename
        self.agent = agent
        self.reset()
        
    def reset(self,):
        self.words = self.initialize_words(self.filename)
    
    def initialize_words(self, filename: str,):
        assert os.path.exists(filename), f"File {filename} does not exist"
        
        with open(filename) as file:
            lines = {line.rstrip() for line in file}
        return lines
    
    def eval_guess(self, guess: str, word: str):
        assert len(guess) == len(word), f"Guess and target word must have same length."\
                                        f" {guess} is not the same length as {word}"
        result = []
        for i,g in enumerate(guess):
            if word[i] == g:
                result.append(2)
            elif g in word:
                result.append(1)
            else:
                result.append(0)

        return result
    
    def single_test(self, word: str = None):
        if not word:
            word = random.choice(tuple(self.words))
        else:
            assert len(word) == 5, f"Test words must have lenght 5. {word} has length {len(word)}"
            assert set([word]) <= self.words, f"Test word not in word list consider adding." \
                                            " Agent won't guess words outside the word list"
        # TODO: test if agent has correct methods
        history = []
        self.agent.reset()
        success = False
        for t in range(6):
            guess = self.agent.get_guess()
            result = self.eval_guess(guess, word)
            self.agent.handle_result(guess, result)
            history.append({guess:result})
            if result == [2,2,2,2,2]:
                success = True
                break
        return success, word, history
    
    def full_test(self,):
        test_words = list(self.words)
        random.shuffle(test_words)
        
        total_score = 0
        total_history = {}
        total_fails = 0
        
        f = IntProgress(min=0, max=len(test_words)) # instantiate the bar
        display(f)
        
        for test_word in test_words:
            success, _, history = self.single_test(word = test_word)
            total_score += len(history)
            total_fails += not success
            total_history[test_word] = history
            print(success)
            f.value += 1
        
        print(f"The agent got a total score of {total_score}/{6*len(test_words)}")
        print(f"That's an average score of {total_score/len(test_words)}/6")
        print(f"The agent failed {total_fails} times")
        return total_score, total_history


# -

from test import Tester

a = Agent()
t = Tester(a)

t.single_test("cater")

t.full_test()

# need to improve words like hates
#
# need to optimize code




