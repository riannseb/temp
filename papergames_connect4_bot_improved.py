# papergames_connect4_bot_fast.py
# Fast and smart Connect4 bot - optimized for speed without sacrificing intelligence

import time
import re
from typing import List, Optional, Tuple, Dict
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PWTimeout

ROWS, COLS = 6, 7
WIN_SCORE = 10000000

def sleep(a=0.2):
    time.sleep(a)

# ---------------- DOM helpers ----------------
def read_board(page) -> List[List[int]]:
    """Read board state: 0=empty, 1=light, 2=dark"""
    board = [[0]*COLS for _ in range(ROWS)]
    for r in range(1, ROWS+1):
        for c in range(1, COLS+1):
            sel = f".grid-item.cell-{r}-{c}"
            try:
                el = page.query_selector(sel)
                if not el:
                    continue
                if el.query_selector(".circle-light"):
                    board_row = ROWS - r
                    board[board_row][c-1] = 1
                elif el.query_selector(".circle-dark"):
                    board_row = ROWS - r
                    board[board_row][c-1] = 2
            except Exception:
                continue
    return board

def is_my_turn(page) -> bool:
    """Detect if it's our turn"""
    try:
        if page.query_selector(".animated"):
            return True
        empty_slots = page.query_selector_all(".empty-slot")
        if empty_slots and len(empty_slots) > 0:
            return True
    except Exception:
        pass
    return False

def get_my_color_and_order(page, my_name="dragon") -> Tuple[Optional[str], Optional[int]]:
    """Detect player color and turn order"""
    try:
        players = page.query_selector_all(".player")
        for i, p in enumerate(players, start=1):
            text = p.inner_text().strip() if p else ""
            if my_name in text:
                if p.query_selector(".circle-light"):
                    return "light", i
                if p.query_selector(".circle-dark"):
                    return "dark", i
    except Exception:
        pass
    return None, None

# ---------------- Fast Game Logic ----------------
def valid_moves(board: List[List[int]]) -> List[int]:
    """Get all valid column moves"""
    return [c for c in range(COLS) if board[ROWS-1][c] == 0]

def make_move_sim(board: List[List[int]], col: int, player: int) -> Optional[List[List[int]]]:
    """Simulate a move and return new board"""
    if col < 0 or col >= COLS or board[ROWS-1][col] != 0:
        return None
    new = [row[:] for row in board]
    for r in range(ROWS):
        if new[r][col] == 0:
            new[r][col] = player
            return new
    return None

def check_win_board(board: List[List[int]], player: int) -> bool:
    """Fast win checking"""
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if board[r][c] == player and board[r][c+1] == player and \
               board[r][c+2] == player and board[r][c+3] == player:
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == player and board[r+1][c] == player and \
               board[r+2][c] == player and board[r+3][c] == player:
                return True
    # Diagonal /
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if board[r][c] == player and board[r+1][c+1] == player and \
               board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True
    # Diagonal \
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if board[r][c] == player and board[r-1][c+1] == player and \
               board[r-2][c+2] == player and board[r-3][c+3] == player:
                return True
    return False

def find_winning_move(board: List[List[int]], player: int) -> Optional[int]:
    """Fast check for immediate winning move"""
    for col in valid_moves(board):
        test = make_move_sim(board, col, player)
        if test and check_win_board(test, player):
            return col
    return None

def find_threats(board: List[List[int]], player: int) -> int:
    """Count immediate threats (for fork detection)"""
    count = 0
    for col in valid_moves(board):
        test = make_move_sim(board, col, player)
        if test and check_win_board(test, player):
            count += 1
    return count

def find_fork_move(board: List[List[int]], player: int) -> Optional[int]:
    """Find move that creates double threat"""
    for col in valid_moves(board):
        test = make_move_sim(board, col, player)
        if test and find_threats(test, player) >= 2:
            return col
    return None

def is_trap(board: List[List[int]], col: int, player: int, opp: int) -> bool:
    """Quick trap detection"""
    test = make_move_sim(board, col, player)
    if not test:
        return False
    
    # Find where we placed
    for r in range(ROWS):
        if test[r][col] == player:
            # Check if opponent wins above
            if r + 1 < ROWS and test[r+1][col] == 0:
                opp_test = [row[:] for row in test]
                opp_test[r+1][col] = opp
                if check_win_board(opp_test, opp):
                    return True
            break
    return False

def evaluate_fast(board: List[List[int]], my_player: int) -> int:
    """Fast position evaluation"""
    opp = 3 - my_player
    score = 0
    
    # Center control
    center = COLS // 2
    for r in range(ROWS):
        if board[r][center] == my_player:
            score += 25
        elif board[r][center] == opp:
            score -= 20
    
    # Count 3-in-a-rows with space
    def count_threes(player):
        count = 0
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS-3):
                window = [board[r][c+i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        # Vertical
        for c in range(COLS):
            for r in range(ROWS-3):
                window = [board[r+i][c] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        # Diagonals
        for r in range(ROWS-3):
            for c in range(COLS-3):
                window = [board[r+i][c+i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        for r in range(3, ROWS):
            for c in range(COLS-3):
                window = [board[r-i][c+i] for i in range(4)]
                if window.count(player) == 3 and window.count(0) == 1:
                    count += 1
        return count
    
    score += count_threes(my_player) * 100
    score -= count_threes(opp) * 120
    
    # Count 2-in-a-rows
    def count_twos(player):
        count = 0
        for r in range(ROWS):
            for c in range(COLS-3):
                window = [board[r][c+i] for i in range(4)]
                if window.count(player) == 2 and window.count(0) == 2:
                    count += 1
        return count
    
    score += count_twos(my_player) * 10
    score -= count_twos(opp) * 12
    
    return score

def minimax_fast(board: List[List[int]], depth: int, alpha: int, beta: int, 
                 maximizing: bool, my_player: int) -> Tuple[int, Optional[int]]:
    """Fast minimax with aggressive pruning"""
    
    opp_player = 3 - my_player
    moves = valid_moves(board)
    
    if depth == 0 or not moves:
        return evaluate_fast(board, my_player), None
    
    # Terminal checks
    if check_win_board(board, my_player):
        return WIN_SCORE - depth, None
    if check_win_board(board, opp_player):
        return -WIN_SCORE + depth, None
    
    # Move ordering - center first
    center = COLS // 2
    moves.sort(key=lambda c: abs(c - center))
    
    best_col = moves[0]
    
    if maximizing:
        max_eval = -float('inf')
        for col in moves:
            new_board = make_move_sim(board, col, my_player)
            if new_board is None:
                continue
            eval_score, _ = minimax_fast(new_board, depth - 1, alpha, beta, False, my_player)
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_col
    else:
        min_eval = float('inf')
        for col in moves:
            new_board = make_move_sim(board, col, opp_player)
            if new_board is None:
                continue
            eval_score, _ = minimax_fast(new_board, depth - 1, alpha, beta, True, my_player)
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_col

def choose_move_fast(board: List[List[int]], my_player: int, opp_player: int) -> int:
    """Fast move selection with critical checks only"""
    
    moves = valid_moves(board)
    if not moves:
        return 3
    
    total_pieces = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != 0)
    
    # Opening book
    if total_pieces == 0:
        return 3
    if total_pieces <= 2:
        if 3 in moves:
            return 3
        return moves[0]
    
    # 1. Win immediately
    win_move = find_winning_move(board, my_player)
    if win_move is not None:
        return win_move
    
    # 2. Block opponent win
    block_move = find_winning_move(board, opp_player)
    if block_move is not None:
        return block_move
    
    # 3. Create fork
    fork_move = find_fork_move(board, my_player)
    if fork_move is not None:
        return fork_move
    
    # 4. Block opponent fork
    opp_fork = find_fork_move(board, opp_player)
    if opp_fork is not None:
        return opp_fork
    
    # 5. Filter traps
    safe_moves = [m for m in moves if not is_trap(board, m, my_player, opp_player)]
    if safe_moves:
        moves = safe_moves
    
    # 6. Quick minimax - adaptive depth
    if total_pieces < 12:
        depth = 5  # Early game
    elif total_pieces < 24:
        depth = 4  # Mid game
    else:
        depth = 6  # End game (fewer moves to check)
    
    _, best_move = minimax_fast(board, depth, -float('inf'), float('inf'), True, my_player)
    
    if best_move is not None and best_move in moves:
        return best_move
    
    # Fallback: center
    center = COLS // 2
    if center in moves:
        return center
    
    return moves[0]

# ---------------- Page interaction ----------------
def click_column(page, col: int) -> bool:
    """Click to drop piece in column"""
    for r in range(ROWS, 0, -1):
        try:
            el = page.query_selector(f".grid-item.cell-{r}-{col+1} .empty-slot")
            if el:
                el.click(timeout=1000)
                return True
        except Exception:
            pass
    try:
        page.click(f".grid-item.cell-1-{col+1}", timeout=1000)
        return True
    except Exception:
        pass
    return False

def game_over(page) -> Optional[str]:
    """Check if game ended"""
    try:
        if page.query_selector("text=Play again!"):
            return "done"
    except Exception:
        pass
    return None

def click_play_again(page) -> bool:
    """Click Play again button"""
    try:
        page.get_by_role("button", name="Play again!").click(timeout=3000)
        return True
    except Exception:
        try:
            page.click("text=Play again!", timeout=2000)
            return True
        except Exception:
            return False

def play_game(page, my_name="dragon"):
    """Play a single game - fast version"""
    
    max_wait = 15
    while max_wait > 0:
        if page.query_selector(".grid"):
            break
        sleep(0.2)
        max_wait -= 1
    
    sleep(0.5)
    
    my_color, my_order = get_my_color_and_order(page, my_name)
    print(f"  Color: {my_color}, Order: {my_order}")
    
    my_player_num = 1 if my_color == "light" else 2 if my_color == "dark" else None
    opp_num = 2 if my_player_num == 1 else 1
    
    move_count = 0
    failed_attempts = 0
    
    while True:
        board = read_board(page)
        total_pieces = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != 0)
        
        if my_player_num is None and total_pieces > 0:
            my_color, my_order = get_my_color_and_order(page, my_name)
            if my_color:
                my_player_num = 1 if my_color == "light" else 2
                opp_num = 3 - my_player_num
        
        if my_player_num is None:
            my_player_num = 1
            opp_num = 2
        
        if game_over(page):
            return True
        
        if not valid_moves(board):
            print("  Board full")
            return True
        
        # Quick turn detection
        turn_wait = 0
        while turn_wait < 20:
            if is_my_turn(page):
                break
            sleep(0.15)
            turn_wait += 1
            if game_over(page):
                return True
        
        # Fast move selection
        start_time = time.time()
        chosen = choose_move_fast(board, my_player_num, opp_num)
        think_time = time.time() - start_time
        
        if click_column(page, chosen):
            move_count += 1
            failed_attempts = 0
            print(f"  Move {move_count}: Col {chosen} ({think_time:.2f}s)")
            sleep(0.25)
        else:
            failed_attempts += 1
            print(f"  Failed: Col {chosen}")
            
            if failed_attempts > 5:
                print("  Too many failures")
                return False
            
            for alt in valid_moves(board):
                if alt != chosen and click_column(page, alt):
                    print(f"  Fallback: Col {alt}")
                    move_count += 1
                    failed_attempts = 0
                    break
        
        sleep(0.2)

# ---------------- Main ----------------
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://papergames.io/en/")
    sleep(0.5)

    try:
        page.get_by_role("link", name=re.compile(r"Connect 4", re.I)).click(timeout=5000)
    except Exception:
        page.click("text=Connect 4")
    
    sleep(0.5)
    
    try:
        page.get_by_role("button", name=re.compile(r"Play with a friend", re.I)).click(timeout=5000)
    except Exception:
        page.click("text=Play with a friend")
    
    sleep(0.5)
    
    my_name = "dragon"
    try:
        tb = page.get_by_role("textbox", name=re.compile(r"Nickname", re.I))
        tb.fill(my_name)
        sleep(0.2)
        tb.press("Enter")
    except Exception:
        try:
            page.fill("input[name='nickname']", my_name, timeout=2000)
        except Exception:
            pass
    
    sleep(0.4)
    try:
        page.get_by_role("button", name=re.compile(r"Continue", re.I)).click(timeout=4000)
    except Exception:
        pass
    
    game_num = 1
    while True:
        print(f"\n=== Game {game_num} ===")
        
        if play_game(page, my_name):
            sleep(1.0)
            
            if click_play_again(page):
                print("Next game...\n")
                sleep(0.8)
                game_num += 1
            else:
                print("No Play again button")
                break
        else:
            print("Game ended unexpectedly")
            break
        
        if game_num > 100:
            break
    
    try:
        context.close()
        browser.close()
    except Exception:
        pass

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)