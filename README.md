# PaperGames Connect 4 Bot

A Python bot that automatically plays **Connect 4** on [PaperGames.io](https://papergames.io/en/) using Playwright and a fast rule-based/minimax game engine.

The bot:

- Opens PaperGames.io in Chromium
- Navigates to Connect 4
- Starts a “Play with a friend” game
- Reads the board directly from the webpage
- Detects winning moves, blocks, forks, and traps
- Uses alpha-beta minimax for move selection
- Automatically clicks **Play again** after each completed game

## How It Works

The project has two main parts:

### Browser automation

Playwright is used to:

- Open the PaperGames website
- Select Connect 4
- Enter a nickname
- Read the current board state from the page
- Detect when it is the bot’s turn
- Click the selected column
- Restart the game after it ends

### Connect 4 strategy

The bot chooses moves using the following priority:

1. Play an immediate winning move
2. Block an immediate opponent win
3. Create a fork
4. Block an opponent fork
5. Avoid moves that create traps
6. Use minimax with alpha-beta pruning
7. Prefer the center column as a fallback

The minimax search depth changes depending on the stage of the game.

## Requirements

- Python 3.10 or newer
- Playwright
- A Chromium browser installed through Playwright

## Installation

Clone the repository:

```bash
git clone https://github.com/riannseb/temp.git
cd temp
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install Playwright:

```bash
pip install playwright
```

Install the Chromium browser used by Playwright:

```bash
playwright install chromium
```

## Running the Bot

Run:

```bash
python papergames_connect4_bot_fast.py
```

A Chromium window will open and the bot will attempt to start playing automatically.

If your Python file has a different name, replace `papergames_connect4_bot_fast.py` with the actual filename.

## Configuration

### Change the nickname

Inside the `run()` function, change:

```python
my_name = "dragon"
```

For example:

```python
my_name = "my_bot"
```

The same nickname is used to identify the bot’s player color and turn order.



### Change the maximum number of games

The current script stops after 100 games:

```python
if game_num > 100:
    break
```

Change `100` to another number if needed.





