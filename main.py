import os
import string
import pandas as pd
from typing import List

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
        
        for i,r in enumerate(result):
            if r == 0:
               self.remove_words_with_letter(letter = guess[i])
            elif r == 1:
                self.remove_words_correct_letter_in_wrong_spot(letter = guess[i], loc=i)
            elif r == 2:
                self.remove_words_correct_letter_in_correct_spot(letter = guess[i], loc=i)
            else:
                raise  ValueError("Result had unknown value that eluded the assert")
    
    def remove_word_from_words(self, word: str,): #might be unnecessary
        self.words.remove(word)
    
    def remove_words_with_letter(self, letter: str,):
        self.words = {w for w in self.words if letter not in w}
        #self.alphabet.remove(letter) #maybe remove
    
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
        scores = {}
        for c in df.columns:
            scores[c] = df[c].value_counts()
        scores_df = pd.DataFrame(scores)
        
        word_scores = {w: 0 for w in self.words}
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
