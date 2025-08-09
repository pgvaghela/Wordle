# Wordle Game

A Python implementation of the popular Wordle game with a modern GUI and dictionary API integration.

## Features

- **Modern GUI**: Clean, intuitive interface with proper styling and colors
- **Massive Word Bank**: 21,953+ 5-letter words from external source for maximum variety
- **Advanced Word Filtering**: Multi-layer validation ensures only valid English words are used
- **Dictionary API Integration**: Uses the Free Dictionary API to validate user guesses
- **Real-time Validation**: Checks if entered words are valid English words
- **Visual Feedback**: Color-coded feedback (green for correct position, yellow for correct letter wrong position, gray for incorrect)
- **New Game Functionality**: Start a new game at any time
- **Input Validation**: Only allows alphabetic characters and limits to 5 letters
- **Status Updates**: Shows remaining attempts and game status
- **Responsive Design**: Centered window with proper sizing
- **Fallback System**: Built-in word list if external source is unavailable

## Requirements

- Python 3.6+
- tkinter (usually comes with Python)
- requests library

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python wordle.py
   ```

2. The game will load a random 5-letter word
3. Enter your guess in the text field (5 letters only)
4. Press Enter or click "GUESS" to submit
5. The grid will show your guess with color-coded feedback:
   - 🟩 Green: Letter is in the correct position
   - 🟨 Yellow: Letter is in the word but wrong position
   - ⬛ Gray: Letter is not in the word
6. You have 6 attempts to guess the word
7. Click "NEW GAME" to start over

## Game Rules

- Each guess must be a valid 5-letter English word
- Letters are color-coded to show how close your guess is
- You have 6 attempts to guess the correct word
- The game validates words using a dictionary API

## Technical Details

- **Primary Word Source**: External GitHub repository with 21,953+ 5-letter English words
- **Advanced Word Filtering**: Multi-layer validation to ensure only valid English words are used
- **Fallback System**: Built-in list of 528 common 5-letter words if external source fails
- **Dictionary API Integration**: Uses the Free Dictionary API (https://dictionaryapi.dev/) for word validation
- **Caching**: Validated words are cached to reduce API calls
- **Error Handling**: Graceful handling of network issues and API failures
- **Modern GUI**: Clean, responsive interface with proper styling

## Files

- `wordle.py`: Main game file
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file

## Troubleshooting

- If the game doesn't start, make sure you have Python 3.6+ installed
- If you get import errors, run `pip install -r requirements.txt`
- If the API is slow or unavailable, the game will use the fallback word list
- Make sure you have an internet connection for word validation

## Future Enhancements

- Statistics tracking
- Hard mode option
- Share results functionality
- Custom word lists
- Sound effects
- Dark mode theme

Enjoy playing Wordle! 🎮
# Enhanced error handling and performance improvements
