import sys
import random
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import threading
import time


class WordleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Game")
        self.master.configure(bg='#f0f0f0')
        
        # Center the window
        self.center_window()
        
        # Game variables
        self.word_to_guess = ""
        self.attempts = 0
        self.max_attempts = 6
        self.guessed_correctly = False
        self.guess_length = 5
        self.valid_words_cache = set()
        self.loading = True
        
        # Create UI elements
        self.create_widgets()
        
        # Load initial word
        self.load_new_word()
        
    def center_window(self):
        """Center the window on screen"""
        self.master.update_idletasks()
        width = 600
        height = 700
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Title
        title_frame = tk.Frame(self.master, bg='#f0f0f0')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="WORDLE", font=('Arial', 32, 'bold'), 
                              fg='#1a1a1a', bg='#f0f0f0')
        title_label.pack()
        
        # Instructions
        self.instructions = tk.Label(self.master, text="Loading...", font=('Arial', 14),
                                   fg='#666666', bg='#f0f0f0')
        self.instructions.pack(pady=10)
        
        # Create the grid for displaying guesses
        self.guess_frame = tk.Frame(self.master, bg='#f0f0f0')
        self.guess_frame.pack(pady=20)
        
        self.guesses = []
        for i in range(self.max_attempts):
            row = []
            for j in range(self.guess_length):
                label = tk.Label(self.guess_frame, text='', width=4, height=2, 
                               font=('Arial', 20, 'bold'), borderwidth=2, 
                               relief='solid', bg='white', fg='#1a1a1a')
                label.grid(row=i, column=j, padx=3, pady=3)
                row.append(label)
            self.guesses.append(row)
        
        # Input frame
        input_frame = tk.Frame(self.master, bg='#f0f0f0')
        input_frame.pack(pady=20)
        
        # Entry field
        self.guess_entry = tk.Entry(input_frame, font=('Arial', 16), justify='center',
                                  width=15, relief='solid', borderwidth=2)
        self.guess_entry.pack(pady=10)
        self.guess_entry.bind('<Return>', lambda event: self.get_user_guess())
        self.guess_entry.bind('<KeyRelease>', self.on_entry_change)
        
        # Guess button
        self.guess_button = tk.Button(input_frame, text="GUESS", command=self.get_user_guess,
                                     font=('Arial', 14, 'bold'), bg='#538d4e', fg='white',
                                     relief='flat', padx=30, pady=10, cursor='hand2')
        self.guess_button.pack(pady=10)
        
        # New game button
        self.new_game_button = tk.Button(input_frame, text="NEW GAME", command=self.new_game,
                                        font=('Arial', 12), bg='#3a3a3c', fg='white',
                                        relief='flat', padx=20, pady=8, cursor='hand2')
        self.new_game_button.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(self.master, text="", font=('Arial', 12),
                                   fg='#666666', bg='#f0f0f0')
        self.status_label.pack(pady=10)
        
    def on_entry_change(self, event):
        """Handle entry field changes"""
        current_text = self.guess_entry.get().lower()
        # Only allow letters
        filtered_text = ''.join(c for c in current_text if c.isalpha())
        if filtered_text != current_text:
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.insert(0, filtered_text)
        
        # Limit to 5 characters
        if len(filtered_text) > 5:
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.insert(0, filtered_text[:5])
            
    def get_external_word_list(self):
        """Get 5-letter words from external GitHub repository"""
        try:
            print("Fetching words from external source...")
            response = requests.get("https://raw.githubusercontent.com/dwyl/english-words/master/words.txt", timeout=10)
            if response.status_code == 200:
                words = response.text.split('\n')
                five_letter_words = [word.lower() for word in words 
                                   if len(word) == 5 and word.isalpha()]
                
                # Filter out invalid words using multiple criteria
                valid_words = []
                for word in five_letter_words:
                    # Basic validation
                    if (len(word) == 5 and 
                        word.isalpha() and 
                        word.islower() and
                        # Check for common invalid patterns
                        not word.startswith('x') and  # Very rare valid words starting with x
                        not word.startswith('q') and  # Most q words need 'u' after
                        not word.endswith('q') and    # No English words end with q
                        not word.endswith('j') and    # Very rare valid words ending with j
                        not word.endswith('v') and    # Very rare valid words ending with v
                        not word.endswith('z') and    # Very rare valid words ending with z
                        # Check for common invalid combinations
                        'q' not in word[:-1] and     # q should be followed by u (except at end)
                        not (word.count('a') > 2) and # Too many repeated vowels
                        not (word.count('e') > 2) and
                        not (word.count('i') > 2) and
                        not (word.count('o') > 2) and
                        not (word.count('u') > 2) and
                        # Check for common valid English patterns
                        (word in self.get_common_words() or  # Must be in common words list
                         self.is_valid_english_word(word))): # Or pass additional validation
                        valid_words.append(word)
                
                print(f"External source loaded {len(valid_words)} valid 5-letter words")
                return valid_words
            else:
                print(f"Failed to fetch external words: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching external words: {e}")
            return None
    
    def get_common_words(self):
        """Return a set of common 5-letter English words for validation"""
        return {
            'about', 'above', 'abuse', 'actor', 'acute', 'admit', 'adopt', 'adult',
            'after', 'again', 'agent', 'agree', 'ahead', 'alarm', 'album', 'alert',
            'alike', 'alive', 'allow', 'alone', 'along', 'alter', 'among', 'anger',
            'angle', 'angry', 'apart', 'apple', 'apply', 'arena', 'argue', 'arise',
            'array', 'aside', 'asset', 'audio', 'audit', 'avoid', 'award', 'aware',
            'awful', 'basic', 'beach', 'began', 'begin', 'begun', 'being', 'below',
            'bench', 'billy', 'birth', 'black', 'blame', 'blank', 'blind', 'block',
            'blood', 'blow', 'blue', 'board', 'boost', 'booth', 'bound', 'brain',
            'brand', 'bread', 'break', 'breed', 'brief', 'bring', 'broad', 'broke',
            'brown', 'build', 'built', 'buyer', 'cable', 'calif', 'carry', 'catch',
            'cause', 'chain', 'chair', 'chart', 'chase', 'cheap', 'check', 'chest',
            'chief', 'child', 'china', 'chose', 'civil', 'claim', 'class', 'clean',
            'clear', 'click', 'clock', 'close', 'coach', 'coast', 'could', 'count',
            'court', 'cover', 'craft', 'crash', 'cream', 'crime', 'cross', 'crowd',
            'crown', 'crude', 'carry', 'curly', 'curry', 'curse', 'curve', 'cycle',
            'daily', 'dance', 'dated', 'dealt', 'death', 'debut', 'delay', 'depth',
            'doing', 'doubt', 'dozen', 'draft', 'drama', 'drank', 'draw', 'drawn',
            'dream', 'dress', 'drill', 'drink', 'drive', 'drove', 'dying', 'eager',
            'early', 'earth', 'eight', 'elite', 'empty', 'enemy', 'enjoy', 'enter',
            'entry', 'equal', 'error', 'event', 'every', 'exact', 'exist', 'extra',
            'faith', 'false', 'fault', 'fiber', 'field', 'fifth', 'fifty', 'fight',
            'final', 'first', 'fixed', 'flash', 'fleet', 'floor', 'fluid', 'focus',
            'force', 'forth', 'forty', 'forum', 'found', 'frame', 'frank', 'fraud',
            'fresh', 'front', 'fruit', 'fully', 'funny', 'giant', 'given', 'glass',
            'globe', 'going', 'grace', 'grade', 'grand', 'grant', 'grass', 'grave',
            'great', 'green', 'gross', 'group', 'grown', 'guard', 'guess', 'guest',
            'guide', 'happy', 'harry', 'heart', 'heavy', 'hence', 'henry', 'horse',
            'hotel', 'house', 'human', 'ideal', 'image', 'index', 'inner', 'input',
            'issue', 'japan', 'jimmy', 'joint', 'jones', 'judge', 'known', 'label',
            'large', 'laser', 'later', 'laugh', 'layer', 'learn', 'lease', 'least',
            'leave', 'legal', 'level', 'lewis', 'light', 'limit', 'links', 'lives',
            'local', 'loose', 'lower', 'lucky', 'lunch', 'lying', 'magic', 'major',
            'maker', 'march', 'maria', 'match', 'maybe', 'mayor', 'meant', 'media',
            'metal', 'might', 'minor', 'minus', 'mixed', 'model', 'money', 'month',
            'moral', 'motor', 'mount', 'mouse', 'mouth', 'moved', 'movie', 'music',
            'needs', 'never', 'newly', 'night', 'noise', 'north', 'noted', 'novel',
            'nurse', 'occur', 'ocean', 'offer', 'often', 'order', 'other', 'ought',
            'paint', 'panel', 'paper', 'party', 'peace', 'peter', 'phase', 'phone',
            'photo', 'piece', 'pilot', 'pitch', 'place', 'plain', 'plane', 'plant',
            'plate', 'point', 'pound', 'power', 'press', 'price', 'pride', 'prime',
            'print', 'prior', 'prize', 'proof', 'proud', 'prove', 'queen', 'quick',
            'quiet', 'quite', 'radio', 'raise', 'range', 'rapid', 'ratio', 'reach',
            'ready', 'realm', 'rebel', 'refer', 'relax', 'relay', 'renal', 'renew',
            'reply', 'rider', 'ridge', 'rifle', 'right', 'rigid', 'rigor', 'rival',
            'river', 'robin', 'roger', 'roman', 'rough', 'round', 'route', 'royal',
            'rural', 'scale', 'scene', 'scope', 'score', 'sense', 'serve', 'seven',
            'shall', 'shape', 'share', 'sharp', 'sheet', 'shelf', 'shell', 'shift',
            'shirt', 'shock', 'shoot', 'short', 'shown', 'sight', 'since', 'sixth',
            'sixty', 'sized', 'skill', 'sleep', 'slide', 'small', 'smart', 'smile',
            'smith', 'smoke', 'solid', 'solve', 'sorry', 'sound', 'south', 'space',
            'spare', 'speak', 'speed', 'spend', 'spent', 'split', 'spoke', 'sport',
            'staff', 'stage', 'stake', 'stand', 'start', 'state', 'steam', 'steel',
            'steep', 'steer', 'steve', 'stick', 'still', 'stock', 'stone', 'stood',
            'store', 'storm', 'story', 'strip', 'stuck', 'study', 'stuff', 'style',
            'sugar', 'suite', 'super', 'sweet', 'table', 'taken', 'taste', 'taxes',
            'teach', 'teeth', 'terry', 'texas', 'thank', 'theft', 'their', 'theme',
            'there', 'these', 'thick', 'thing', 'think', 'third', 'those', 'three',
            'threw', 'throw', 'thumb', 'tiger', 'tight', 'timer', 'tired', 'title',
            'today', 'topic', 'total', 'touch', 'tough', 'tower', 'track', 'trade',
            'train', 'treat', 'trend', 'trial', 'tribe', 'trick', 'tried', 'tries',
            'truck', 'truly', 'trunk', 'trust', 'truth', 'twice', 'under', 'undue',
            'union', 'unity', 'until', 'upper', 'upset', 'urban', 'usage', 'usual',
            'valid', 'value', 'video', 'virus', 'visit', 'vital', 'vocal', 'voice',
            'waste', 'watch', 'water', 'wheel', 'where', 'which', 'while', 'white',
            'whole', 'whose', 'woman', 'women', 'world', 'worry', 'worse', 'worst',
            'worth', 'would', 'wound', 'write', 'wrong', 'wrote', 'yield', 'young',
            'youth', 'hello', 'world', 'about', 'above', 'abuse', 'actor', 'acute',
            'admit', 'adopt', 'adult', 'after', 'again', 'agent', 'agree', 'ahead',
            'alarm', 'album', 'alert', 'alike', 'alive', 'allow', 'alone', 'along',
            'alter', 'among', 'anger', 'angle', 'angry', 'apart', 'apple', 'apply',
            'arena', 'argue', 'arise', 'array', 'aside', 'asset', 'audio', 'audit',
            'avoid', 'award', 'aware', 'awful', 'basic', 'beach', 'began', 'begin',
            'begun', 'being', 'below', 'bench', 'billy', 'birth', 'black', 'blame',
            'blank', 'blind', 'block', 'blood', 'blow', 'blue', 'board', 'boost',
            'booth', 'bound', 'brain', 'brand', 'bread', 'break', 'breed', 'brief',
            'bring', 'broad', 'broke', 'brown', 'build', 'built', 'buyer', 'cable',
            'calif', 'carry', 'catch', 'cause', 'chain', 'chair', 'chart', 'chase',
            'cheap', 'check', 'chest', 'chief', 'child', 'china', 'chose', 'civil',
            'claim', 'class', 'clean', 'clear', 'click', 'clock', 'close', 'coach',
            'coast', 'could', 'count', 'court', 'cover', 'craft', 'crash', 'cream',
            'crime', 'cross', 'crowd', 'crown', 'crude', 'carry', 'curly', 'curry',
            'curse', 'curve', 'cycle', 'daily', 'dance', 'dated', 'dealt', 'death',
            'debut', 'delay', 'depth', 'doing', 'doubt', 'dozen', 'draft', 'drama',
            'drank', 'draw', 'drawn', 'dream', 'dress', 'drill', 'drink', 'drive',
            'drove', 'dying', 'eager', 'early', 'earth', 'eight', 'elite', 'empty',
            'enemy', 'enjoy', 'enter', 'entry', 'equal', 'error', 'event', 'every',
            'exact', 'exist', 'extra', 'faith', 'false', 'fault', 'fiber', 'field',
            'fifth', 'fifty', 'fight', 'final', 'first', 'fixed', 'flash', 'fleet',
            'floor', 'fluid', 'focus', 'force', 'forth', 'forty', 'forum', 'found',
            'frame', 'frank', 'fraud', 'fresh', 'front', 'fruit', 'fully', 'funny',
            'giant', 'given', 'glass', 'globe', 'going', 'grace', 'grade', 'grand',
            'grant', 'grass', 'grave', 'great', 'green', 'gross', 'group', 'grown',
            'guard', 'guess', 'guest', 'guide', 'happy', 'harry', 'heart', 'heavy',
            'hence', 'henry', 'horse', 'hotel', 'house', 'human', 'ideal', 'image',
            'index', 'inner', 'input', 'issue', 'japan', 'jimmy', 'joint', 'jones',
            'judge', 'known', 'label', 'large', 'laser', 'later', 'laugh', 'layer',
            'learn', 'lease', 'least', 'leave', 'legal', 'level', 'lewis', 'light',
            'limit', 'links', 'lives', 'local', 'loose', 'lower', 'lucky', 'lunch',
            'lying', 'magic', 'major', 'maker', 'march', 'maria', 'match', 'maybe',
            'mayor', 'meant', 'media', 'metal', 'might', 'minor', 'minus', 'mixed',
            'model', 'money', 'month', 'moral', 'motor', 'mount', 'mouse', 'mouth',
            'moved', 'movie', 'music', 'needs', 'never', 'newly', 'night', 'noise',
            'north', 'noted', 'novel', 'nurse', 'occur', 'ocean', 'offer', 'often',
            'order', 'other', 'ought', 'paint', 'panel', 'paper', 'party', 'peace',
            'peter', 'phase', 'phone', 'photo', 'piece', 'pilot', 'pitch', 'place',
            'plain', 'plane', 'plant', 'plate', 'point', 'pound', 'power', 'press',
            'price', 'pride', 'prime', 'print', 'prior', 'prize', 'proof', 'proud',
            'prove', 'queen', 'quick', 'quiet', 'quite', 'radio', 'raise', 'range',
            'rapid', 'ratio', 'reach', 'ready', 'realm', 'rebel', 'refer', 'relax',
            'relay', 'renal', 'renew', 'reply', 'rider', 'ridge', 'rifle', 'right',
            'rigid', 'rigor', 'rival', 'river', 'robin', 'roger', 'roman', 'rough',
            'round', 'route', 'royal', 'rural', 'scale', 'scene', 'scope', 'score',
            'sense', 'serve', 'seven', 'shall', 'shape', 'share', 'sharp', 'sheet',
            'shelf', 'shell', 'shift', 'shirt', 'shock', 'shoot', 'short', 'shown',
            'sight', 'since', 'sixth', 'sixty', 'sized', 'skill', 'sleep', 'slide',
            'small', 'smart', 'smile', 'smith', 'smoke', 'solid', 'solve', 'sorry',
            'sound', 'south', 'space', 'spare', 'speak', 'speed', 'spend', 'spent',
            'split', 'spoke', 'sport', 'staff', 'stage', 'stake', 'stand', 'start',
            'state', 'steam', 'steel', 'steep', 'steer', 'steve', 'stick', 'still',
            'stock', 'stone', 'stood', 'store', 'storm', 'story', 'strip', 'stuck',
            'study', 'stuff', 'style', 'sugar', 'suite', 'super', 'sweet', 'table',
            'taken', 'taste', 'taxes', 'teach', 'teeth', 'terry', 'texas', 'thank',
            'theft', 'their', 'theme', 'there', 'these', 'thick', 'thing', 'think',
            'third', 'those', 'three', 'threw', 'throw', 'thumb', 'tiger', 'tight',
            'timer', 'tired', 'title', 'today', 'topic', 'total', 'touch', 'tough',
            'tower', 'track', 'trade', 'train', 'treat', 'trend', 'trial', 'tribe',
            'trick', 'tried', 'tries', 'truck', 'truly', 'trunk', 'trust', 'truth',
            'twice', 'under', 'undue', 'union', 'unity', 'until', 'upper', 'upset',
            'urban', 'usage', 'usual', 'valid', 'value', 'video', 'virus', 'visit',
            'vital', 'vocal', 'voice', 'waste', 'watch', 'water', 'wheel', 'where',
            'which', 'while', 'white', 'whole', 'whose', 'woman', 'women', 'world',
            'worry', 'worse', 'worst', 'worth', 'would', 'wound', 'write', 'wrong',
            'wrote', 'yield', 'young', 'youth'
        }
    
    def is_valid_english_word(self, word):
        """Additional validation for English words"""
        # Check against dictionary API
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=2)
            return response.status_code == 200
        except:
            # If API fails, use basic English word patterns
            return self.is_english_pattern(word)
    
    def is_english_pattern(self, word):
        """Check if word follows basic English patterns"""
        # Common English word patterns
        common_patterns = [
            # Common word endings
            word.endswith('ing'), word.endswith('ed'), word.endswith('er'),
            word.endswith('ly'), word.endswith('al'), word.endswith('ic'),
            word.endswith('ous'), word.endswith('ful'), word.endswith('less'),
            # Common word beginnings
            word.startswith('un'), word.startswith('re'), word.startswith('in'),
            word.startswith('im'), word.startswith('dis'), word.startswith('en'),
            # Common letter combinations
            'th' in word, 'ch' in word, 'sh' in word, 'ph' in word,
            'wh' in word, 'ck' in word, 'ng' in word, 'st' in word,
            # Vowel-consonant patterns
            any(v + c in word for v in 'aeiou' for c in 'bcdfghjklmnpqrstvwxyz'),
            # Common English words
            word in ['hello', 'world', 'about', 'above', 'abuse', 'actor', 'acute']
        ]
        
        return any(common_patterns)
    
    def get_fallback_words(self):
        """Fallback word list if external source fails"""
        return [
            'about', 'above', 'abuse', 'actor', 'acute', 'admit', 'adopt', 'adult',
            'after', 'again', 'agent', 'agree', 'ahead', 'alarm', 'album', 'alert',
            'alike', 'alive', 'allow', 'alone', 'along', 'alter', 'among', 'anger',
            'angle', 'angry', 'apart', 'apple', 'apply', 'arena', 'argue', 'arise',
            'array', 'aside', 'asset', 'audio', 'audit', 'avoid', 'award', 'aware',
            'awful', 'basic', 'beach', 'began', 'begin', 'begun', 'being', 'below',
            'bench', 'billy', 'birth', 'black', 'blame', 'blank', 'blind', 'block',
            'blood', 'blow', 'blue', 'board', 'boost', 'booth', 'bound', 'brain',
            'brand', 'bread', 'break', 'breed', 'brief', 'bring', 'broad', 'broke',
            'brown', 'build', 'built', 'buyer', 'cable', 'calif', 'carry', 'catch',
            'cause', 'chain', 'chair', 'chart', 'chase', 'cheap', 'check', 'chest',
            'chief', 'child', 'china', 'chose', 'civil', 'claim', 'class', 'clean',
            'clear', 'click', 'clock', 'close', 'coach', 'coast', 'could', 'count',
            'court', 'cover', 'craft', 'crash', 'cream', 'crime', 'cross', 'crowd',
            'crown', 'crude', 'carry', 'curly', 'curry', 'curse', 'curve', 'cycle',
            'daily', 'dance', 'dated', 'dealt', 'death', 'debut', 'delay', 'depth',
            'doing', 'doubt', 'dozen', 'draft', 'drama', 'drank', 'draw', 'drawn',
            'dream', 'dress', 'drill', 'drink', 'drive', 'drove', 'dying', 'eager',
            'early', 'earth', 'eight', 'elite', 'empty', 'enemy', 'enjoy', 'enter',
            'entry', 'equal', 'error', 'event', 'every', 'exact', 'exist', 'extra',
            'faith', 'false', 'fault', 'fiber', 'field', 'fifth', 'fifty', 'fight',
            'final', 'first', 'fixed', 'flash', 'fleet', 'floor', 'fluid', 'focus',
            'force', 'forth', 'forty', 'forum', 'found', 'frame', 'frank', 'fraud',
            'fresh', 'front', 'fruit', 'fully', 'funny', 'giant', 'given', 'glass',
            'globe', 'going', 'grace', 'grade', 'grand', 'grant', 'grass', 'grave',
            'great', 'green', 'gross', 'group', 'grown', 'guard', 'guess', 'guest',
            'guide', 'happy', 'harry', 'heart', 'heavy', 'hence', 'henry', 'horse',
            'hotel', 'house', 'human', 'ideal', 'image', 'index', 'inner', 'input',
            'issue', 'japan', 'jimmy', 'joint', 'jones', 'judge', 'known', 'label',
            'large', 'laser', 'later', 'laugh', 'layer', 'learn', 'lease', 'least',
            'leave', 'legal', 'level', 'lewis', 'light', 'limit', 'links', 'lives',
            'local', 'loose', 'lower', 'lucky', 'lunch', 'lying', 'magic', 'major',
            'maker', 'march', 'maria', 'match', 'maybe', 'mayor', 'meant', 'media',
            'metal', 'might', 'minor', 'minus', 'mixed', 'model', 'money', 'month',
            'moral', 'motor', 'mount', 'mouse', 'mouth', 'moved', 'movie', 'music',
            'needs', 'never', 'newly', 'night', 'noise', 'north', 'noted', 'novel',
            'nurse', 'occur', 'ocean', 'offer', 'often', 'order', 'other', 'ought',
            'paint', 'panel', 'paper', 'party', 'peace', 'peter', 'phase', 'phone',
            'photo', 'piece', 'pilot', 'pitch', 'place', 'plain', 'plane', 'plant',
            'plate', 'point', 'pound', 'power', 'press', 'price', 'pride', 'prime',
            'print', 'prior', 'prize', 'proof', 'proud', 'prove', 'queen', 'quick',
            'quiet', 'quite', 'radio', 'raise', 'range', 'rapid', 'ratio', 'reach',
            'ready', 'realm', 'rebel', 'refer', 'relax', 'relay', 'renal', 'renew',
            'reply', 'rider', 'ridge', 'rifle', 'right', 'rigid', 'rigor', 'rival',
            'river', 'robin', 'roger', 'roman', 'rough', 'round', 'route', 'royal',
            'rural', 'scale', 'scene', 'scope', 'score', 'sense', 'serve', 'seven',
            'shall', 'shape', 'share', 'sharp', 'sheet', 'shelf', 'shell', 'shift',
            'shirt', 'shock', 'shoot', 'short', 'shown', 'sight', 'since', 'sixth',
            'sixty', 'sized', 'skill', 'sleep', 'slide', 'small', 'smart', 'smile',
            'smith', 'smoke', 'solid', 'solve', 'sorry', 'sound', 'south', 'space',
            'spare', 'speak', 'speed', 'spend', 'spent', 'split', 'spoke', 'sport',
            'staff', 'stage', 'stake', 'stand', 'start', 'state', 'steam', 'steel',
            'steep', 'steer', 'steve', 'stick', 'still', 'stock', 'stone', 'stood',
            'store', 'storm', 'story', 'strip', 'stuck', 'study', 'stuff', 'style',
            'sugar', 'suite', 'super', 'sweet', 'table', 'taken', 'taste', 'taxes',
            'teach', 'teeth', 'terry', 'texas', 'thank', 'theft', 'their', 'theme',
            'there', 'these', 'thick', 'thing', 'think', 'third', 'those', 'three',
            'threw', 'throw', 'thumb', 'tiger', 'tight', 'timer', 'tired', 'title',
            'today', 'topic', 'total', 'touch', 'tough', 'tower', 'track', 'trade',
            'train', 'treat', 'trend', 'trial', 'tribe', 'trick', 'tried', 'tries',
            'truck', 'truly', 'trunk', 'trust', 'truth', 'twice', 'under', 'undue',
            'union', 'unity', 'until', 'upper', 'upset', 'urban', 'usage', 'usual',
            'valid', 'value', 'video', 'virus', 'visit', 'vital', 'vocal', 'voice',
            'waste', 'watch', 'water', 'wheel', 'where', 'which', 'while', 'white',
            'whole', 'whose', 'woman', 'women', 'world', 'worry', 'worse', 'worst',
            'worth', 'would', 'wound', 'write', 'wrong', 'wrote', 'yield', 'young',
            'youth'
        ]
            
    def load_new_word(self):
        """Load a new word from external source or fallback"""
        # Try external source first
        word_list = self.get_external_word_list()
        
        if word_list is None or len(word_list) == 0:
            print("Using fallback word list")
            word_list = self.get_fallback_words()
        
        # Select a random word
        self.word_to_guess = random.choice(word_list)
        self.valid_words_cache = set(word_list)
        self.loading = False
        
        # Update UI immediately
        self.update_ui_after_load()
        
    def update_ui_after_load(self):
        """Update UI after word is loaded"""
        word_count = len(self.valid_words_cache)
        self.instructions.config(text="Guess the 5-letter word:")
        self.status_label.config(text=f"Word loaded! {word_count} words available. You have {self.max_attempts} attempts.")
        self.guess_entry.config(state='normal')
        self.guess_button.config(state='normal')
        
    def validate_word(self, word):
        """Validate if a word exists using the dictionary API"""
        if word in self.valid_words_cache:
            return True
            
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=3)
            if response.status_code == 200:
                self.valid_words_cache.add(word)
                return True
            else:
                return False
        except:
            # If API fails, assume it's valid if it's 5 letters and all alphabetic
            return len(word) == 5 and word.isalpha()
    
    def get_user_guess(self):
        """Get and process user's guess"""
        if self.loading:
            messagebox.showinfo("Loading", "Please wait while the word is being loaded...")
            return
            
        # Get user's guess and convert to lowercase
        guess = self.guess_entry.get().lower().strip()
        
        # Check if the guess is valid length
        if len(guess) != self.guess_length:
            messagebox.showerror("Invalid Guess", "Please enter a 5-letter word.")
            return
        
        # Check if the word is valid
        if not self.validate_word(guess):
            messagebox.showerror("Invalid Word", "That's not a valid word. Please try again.")
            return
        
        # Clear the entry field for the next guess
        self.guess_entry.delete(0, tk.END)
        
        # Check if the guess matches the word
        if guess == self.word_to_guess:
            self.guessed_correctly = True
            self.update_grid(guess)
            self.end_game("🎉 Congratulations! You guessed the word!")
        else:
            self.update_grid(guess)
            self.attempts += 1
            
            # Update status
            remaining = self.max_attempts - self.attempts
            if remaining > 0:
                self.status_label.config(text=f"Try again! {remaining} attempts remaining.")
            else:
                self.status_label.config(text="")
        
        # Check if the user has run out of attempts
        if self.attempts >= self.max_attempts and not self.guessed_correctly:
            self.end_game(f"😔 Game Over! The correct word was '{self.word_to_guess.upper()}'.")
    
    def update_grid(self, guess):
        """Update the grid with the current guess and color the boxes"""
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
                label.config(bg='#538d4e')  # Green
            elif progress[i] == 'yellow':
                label.config(bg='#b59f3b', fg='white')  # Yellow
            else:
                label.config(bg='#3a3a3c')  # Gray
    
    def end_game(self, message):
        """End the game and display final message"""
        # Display the final message
        messagebox.showinfo("Game Over", message)
        
        # Disable further guesses
        self.guess_button.config(state=tk.DISABLED)
        self.guess_entry.config(state=tk.DISABLED)
        
        # Update status
        self.status_label.config(text="Game finished! Click 'NEW GAME' to play again.")
    
    def new_game(self):
        """Start a new game"""
        # Reset game variables
        self.word_to_guess = ""
        self.attempts = 0
        self.guessed_correctly = False
        self.loading = True
        
        # Clear the grid
        for i in range(self.max_attempts):
            for j in range(self.guess_length):
                self.guesses[i][j].config(text='', bg='white', fg='#1a1a1a')
        
        # Reset UI
        self.instructions.config(text="Loading...")
        self.status_label.config(text="")
        self.guess_entry.config(state='disabled')
        self.guess_button.config(state='disabled')
        self.guess_entry.delete(0, tk.END)
        
        # Load new word
        self.load_new_word()

# Create the main window and run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = WordleGUI(root)
    root.mainloop()
