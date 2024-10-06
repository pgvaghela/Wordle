import sys
import random
import tkinter as tk
from tkinter import messagebox

sys.path.append('./files')

from wordle_words import word_list, valid_guesses


class WordleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Game")

        # Game variables
        self.word_to_guess = random.choice(word_list)
        self.attempts = 0
        self.max_attempts = 6
        self.guessed_correctly = False
        self.guess_length = 5

        # Create UI elements
        self.instructions = tk.Label(master, text="Guess the 5-letter word:")
        self.instructions.pack()

        # Create the grid for displaying guesses
        self.guess_frame = tk.Frame(master)
        self.guess_frame.pack()

        self.guesses = []

        for i in range(self.max_attempts):
            row = []
            for j in range(self.guess_length):
                label = tk.Label(self.guess_frame, text='', width=4, height=2, font=('Helvetica', 18), borderwidth=1, relief='solid')
                label.grid(row=i, column=j, padx=5, pady=5)
                row.append(label)
            self.guesses.append(row)

        # Create the entry field and guess button
        self.guess_entry = tk.Entry(master, font=('Helvetica', 18), justify='center')
        self.guess_entry.pack(pady=10)

        self.guess_button = tk.Button(master, text="Guess", command=self.get_user_guess, font=('Helvetica', 14))
        self.guess_button.pack()

    def get_user_guess(self):
        # Get user's guess and convert to lowercase
        guess = self.guess_entry.get().lower()

        # Check if the guess is valid
        if len(guess) != self.guess_length or guess not in valid_guesses:
            messagebox.showerror("Invalid Guess", "Please enter a valid 5-letter word.")
            return

        # Clear the entry field for the next guess
        self.guess_entry.delete(0, tk.END)

        # Check if the guess matches the word
        if guess == self.word_to_guess:
            self.guessed_correctly = True
            self.update_grid(guess)
            self.end_game("Congratulations! You guessed the word!")
        else:
            self.update_grid(guess)
            self.attempts += 1

        # Check if the user has run out of attempts
        if self.attempts >= self.max_attempts and not self.guessed_correctly:
            self.end_game(f"The correct word was {self.word_to_guess}. Try again!")

    def update_grid(self, guess):
        # Create a list to track which letters have been marked as correct
        word_to_guess_copy = list(self.word_to_guess)
        progress = [''] * self.guess_length

        # First pass: Mark all green letters (correct position)
        for i in range(self.guess_length):
            if guess[i] == self.word_to_guess[i]:
                progress[i] = 'green'
                word_to_guess_copy[i] = None  # Mark this letter as accounted for

        # Second pass: Mark yellow letters (correct letter, wrong position)
        for i in range(self.guess_length):
            if progress[i] == '':  # Only consider letters not already marked as green
                if guess[i] in word_to_guess_copy:
                    progress[i] = 'yellow'
                    word_to_guess_copy[word_to_guess_copy.index(guess[i])] = None  # Mark this occurrence as used
                else:
                    progress[i] = 'gray'

        # Update the grid with the current guess and color the boxes based on correctness
        for i, letter in enumerate(guess):
            label = self.guesses[self.attempts][i]
            label.config(text=letter.upper(), fg='white')

            if progress[i] == 'green':
                label.config(bg='green')
            elif progress[i] == 'yellow':
                label.config(bg='yellow', fg='black')
            else:
                label.config(bg='gray')

    def end_game(self, message):
        # Display the final message and disable further guesses
        messagebox.showinfo("Game Over", message)
        self.guess_button.config(state=tk.DISABLED)
        self.guess_entry.config(state=tk.DISABLED)


# Create the main window and run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = WordleGUI(root)
    root.mainloop()
