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
