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

### Run in headless mode

By default, the browser is visible:

```python
browser = playwright.chromium.launch(headless=False)
```

To run without showing the browser window:

```python
browser = playwright.chromium.launch(headless=True)
```

Running visibly is recommended while testing because website layout or selector changes can be easier to diagnose.

### Change the maximum number of games

The current script stops after 100 games:

```python
if game_num > 100:
    break
```

Change `100` to another number if needed.

## Project Structure

```text
.
├── papergames_connect4_bot_fast.py
├── README.md
└── .gitignore
```

A recommended `.gitignore` is:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.DS_Store
```

## Important Notes

- The bot relies on the current HTML structure and CSS selectors used by PaperGames.io.
- If the website changes its page layout, class names, text, or buttons, some selectors may need to be updated.
- Turn detection is based on webpage elements such as `.animated` and `.empty-slot`.
- The script assumes that light pieces correspond to player `1` and dark pieces correspond to player `2`.
- Network speed and animations may affect browser timing.

## Troubleshooting

### `ModuleNotFoundError: No module named 'playwright'`

Install Playwright:

```bash
pip install playwright
playwright install chromium
```

### Browser does not open

Make sure Chromium was installed:

```bash
playwright install chromium
```

### The bot opens the page but does not click correctly

PaperGames.io may have changed its page structure. Check selectors such as:

```python
.grid-item
.empty-slot
.player
.circle-light
.circle-dark
```

You may also need to increase Playwright timeouts or sleep durations.

### The bot identifies the wrong player

Make sure the nickname in:

```python
my_name = "dragon"
```

matches the nickname entered on the website.

### The bot makes moves too quickly

Increase values such as:

```python
sleep(0.25)
sleep(0.2)
```

This can help when the website has slower animations or network delays.

## Limitations

- The evaluation function only counts horizontal two-in-a-row patterns.
- The bot does not use a transposition table or persistent opening database.
- The turn detector may sometimes identify a turn too early.
- The automation is tightly coupled to the current PaperGames.io interface.
- The bot is not guaranteed to play a mathematically perfect Connect 4 game at its current search depths.

## Possible Improvements

Potential future improvements include:

- Add a transposition table for faster minimax searches
- Use iterative deepening with a time limit
- Improve diagonal and vertical pattern evaluation
- Detect the last move instead of repeatedly reading the entire board
- Add stronger fork and trap analysis
- Add logging and screenshots when an interaction fails
- Move CSS selectors into a configuration file
- Add automated tests for board logic
- Package dependencies in a `requirements.txt` file

## Responsible Use

Use this project for learning, experimentation, and browser-automation practice. Make sure your use follows the website’s terms and does not disrupt games or other users.

## License

No license has been selected yet. Add a `LICENSE` file before allowing reuse or redistribution.
