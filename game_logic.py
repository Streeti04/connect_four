import random
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait

# Spielfeld-Konstanten
ROWS = 6  # Anzahl der Zeilen
COLS = 7  # Anzahl der Spalten
PLAYER = '🔴'  # Symbol für den menschlichen Spieler
AI = '🟡'  # Symbol für den KI-Spieler
EMPTY = ' '  # Symbol für leere Felder

def create_board():
    """
    Erstellt ein leeres Spielfeld.
    
    Rückgabe:
        Ein 2D-Array mit ROWS×COLS Größe, gefüllt mit EMPTY.
    """
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def drop_piece(board, row, col, piece):
    """
    Setzt einen Spielstein in das Spielfeld.
    
    Parameter:
        board: Das Spielfeld
        row: Die Zeile
        col: Die Spalte
        piece: Der Spielstein (PLAYER oder AI)
    """
    board[row][col] = piece

def is_valid_location(board, col):
    """
    Überprüft, ob die Spalte col im Spielfeld board noch Platz hat.
    
    Parameter:
        board: Das Spielfeld
        col: Die zu prüfende Spalte
        
    Rückgabe:
        True, wenn die Spalte noch nicht voll ist, sonst False.
    """
    return board[ROWS-1][col] == EMPTY

def get_next_open_row(board, col):
    """
    Gibt die nächste freie Zeile in der Spalte col zurück.
    
    Parameter:
        board: Das Spielfeld
        col: Die Spalte
        
    Rückgabe:
        Der Index der untersten freien Zeile in der angegebenen Spalte.
    """
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r

def winning_move(board, piece):
    """
    Überprüft, ob ein Spieler gewonnen hat.
    
    Parameter:
        board: Das Spielfeld
        piece: Der zu prüfende Spielstein (PLAYER oder AI)
        
    Rückgabe:
        True, wenn der Spieler mit dem angegebenen Spielstein gewonnen hat,
        sonst False.
    """
    # Horizontale Überprüfung
    for c in range(COLS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Vertikale Überprüfung
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Diagonale Überprüfung (ansteigend)
    for c in range(COLS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Diagonale Überprüfung (abfallend)
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False

def evaluate_window(window, piece):
    """
    Bewertet ein Fenster von vier Zellen im Spielfeld für den Minmax-Algorithmus.
    
    Parameter:
        window: Eine Liste von vier Spielsteinen
        piece: Der Spielstein (AI oder PLAYER), für den bewertet wird
        
    Rückgabe:
        Eine Punktzahl, die den Stand der Position angibt.
    """
    score = 0
    opp_piece = PLAYER if piece == AI else AI  # Gegnerischer Spielstein

    # Werte verschiedene Situationen
    if window.count(piece) == 4:  # 4 in einer Reihe = Sieg
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:  # 3 in einer Reihe mit Lücke
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:  # 2 in einer Reihe mit Lücken
        score += 2

    # Blockiere gegnerische Siegchancen
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    """
    Bewertet die aktuelle Position des Spielfelds für den Minmax-Algorithmus.
    
    Parameter:
        board: Das Spielfeld
        piece: Der Spielstein (AI oder PLAYER), für den bewertet wird
        
    Rückgabe:
        Eine Gesamtpunktzahl für die aktuelle Position.
    """
    score = 0

    # Mittlere Spalte bewerten (strategisch wertvoll)
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontale Bewertung
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Vertikale Bewertung
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Diagonale Bewertung (ansteigend)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Diagonale Bewertung (abfallend)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    """
    Überprüft, ob das Spiel beendet ist (Sieg oder Unentschieden).
    
    Parameter:
        board: Das Spielfeld
        
    Rückgabe:
        True, wenn das Spiel beendet ist, sonst False.
    """
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    """
    Minimax-Algorithmus mit Alpha-Beta-Pruning zur Bestimmung des besten Zuges.
    
    Parameter:
        board: Das Spielfeld
        depth: Die aktuelle Suchtiefe
        alpha: Alpha-Wert für Alpha-Beta-Pruning
        beta: Beta-Wert für Alpha-Beta-Pruning
        maximizingPlayer: True, wenn der maximierende Spieler am Zug ist (AI)
        
    Rückgabe:
        Tuple (Spalte, Bewertung) mit dem besten Zug und dessen Bewertung
    """
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    # Basisfall: Maximale Tiefe erreicht oder Endposition
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, 100000000000000)  # AI gewinnt
            elif winning_move(board, PLAYER):
                return (None, -10000000000000)  # Spieler gewinnt
            else:  # Unentschieden (keine weiteren Züge möglich)
                return (None, 0)
        else:  # Maximale Tiefe erreicht
            return (None, score_position(board, AI))
            
    if maximizingPlayer:  # AI ist am Zug (maximierend)
        value = -float('inf')
        column = random.choice(valid_locations)  # Standardwert, falls keine Verbesserung gefunden wird
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = [row[:] for row in board]  # Kopie des Spielfelds erstellen
            drop_piece(b_copy, row, col, AI)  # Testweise Stein setzen
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]  # Bewertung des Zuges ermitteln
            
            if new_score > value:  # Besseren Zug gefunden
                value = new_score
                column = col
                
            alpha = max(alpha, value)  # Alpha-Wert aktualisieren
            if alpha >= beta:  # Beta-Cutoff
                break
                
        return column, value

    else:  # Spieler ist am Zug (minimierend)
        value = float('inf')
        column = random.choice(valid_locations)  # Standardwert, falls keine Verbesserung gefunden wird
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = [row[:] for row in board]  # Kopie des Spielfelds erstellen
            drop_piece(b_copy, row, col, PLAYER)  # Testweise Stein setzen
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]  # Bewertung des Zuges ermitteln
            
            if new_score < value:  # Besseren Zug gefunden (minimierend)
                value = new_score
                column = col
                
            beta = min(beta, value)  # Beta-Wert aktualisieren
            if alpha >= beta:  # Alpha-Cutoff
                break
                
        return column, value

def get_valid_locations(board):
    """
    Ermittelt alle gültigen Spalten, in die ein Spielstein gesetzt werden kann.
        
    Rückgabe:
        Eine Liste der Spaltenindizes, die noch nicht voll sind.
    """
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def draw_piece(motor_a, motor_b, motor_c, row, col, piece,
               max_height: int,
               min_height: int,
               field_width: int):
    """
    Zeichnet einen Spielstein auf dem physischen Spielfeld.
    
    """
    # Berechnung der Zellengröße
    cell_width = field_width / COLS
    cell_height = (max_height - min_height) / ROWS

    # Berechnung der Mitte der Zelle
    x = (col * cell_width) + (cell_width / 2)
    y = (ROWS - 1 - row) * cell_height + min_height + (cell_height / 2)

    # Bewege den Stift an die richtige Position
    motor_b.run_target(500, -x)
    motor_c.run_target(500, y)

    # Zeichne entweder ein X (für Spieler) oder ein Minus (für KI)
    if piece == PLAYER:
        draw_cross(motor_a, motor_b, motor_c)
    else:
        draw_minus(motor_a, motor_b, motor_c)


def draw_cross(motor_a, motor_b, motor_c):
    """
    Zeichnet ein Kreuz (X) für den Spieler.
    
    """
    motor_b.run_angle(200, 40)  # 40° nach rechts bewegen
    motor_a.run_angle(200, -180)  # Stift absenken
    motor_b.run_angle(200, -80)  # 80° nach links bewegen
    motor_b.run_angle(200, 40)  # 40° nach rechts bewegen
    motor_c.run_angle(200, 50)  # 50° nach unten bewegen
    motor_c.run_angle(200, -90)  # 90° nach oben bewegen
    motor_c.run_angle(200, 60)  # 60° nach unten bewegen
    motor_a.run_angle(200, 180)  # Stift anheben

def draw_minus(motor_a, motor_b, motor_c):
    """
    Zeichnet ein Minus (-) für die KI.
    
    """
    motor_a.run_angle(200, -180)  # Stift absenken
    motor_b.run_angle(200, 50)  # 50° nach rechts bewegen
    motor_b.run_angle(200, -80)  # 80° nach links bewegen
    motor_a.run_angle(200, 180)  # Stift anheben

def play_game(motor_a, motor_b, motor_c, max_height, min_height, field_width):
    """
    Steuert den Spielablauf zwischen Spieler und KI.
    
    Parameter:
        motor_a: Motor für den Stift (heben/senken)
        motor_b: Motor für die X-Achse
        motor_c: Motor für die Y-Achse
        max_height: Maximale Höhe des Spielfelds
        min_height: Minimale Höhe des Spielfelds
        field_width: Breite des Spielfelds
    """
    board = create_board()  # Leeres Spielfeld erstellen
    game_over = False  # Spiel läuft
    turn = 0  # 0 für Spieler, 1 für KI

    while not game_over:
        if turn == 0:
            # Spielerzug
            col = player_input_via_ev3()  # Warte auf Eingabe des Spielers über EV3
            
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)  # Ermittle die unterste freie Zeile
                drop_piece(board, row, col, PLAYER)  # Spielstein setzen
                show_board(board)  # Spielfeld im Terminal anzeigen
                
                # Spielstein physisch zeichnen
                draw_piece(motor_a, motor_b, motor_c, row, col, PLAYER,
                           max_height, min_height, field_width)

                # Überprüfe auf Sieg
                if winning_move(board, PLAYER):
                    print("Spieler X gewinnt!")
                    game_over = True

        else:
            # KI-Zug
            col, minimax_score = minimax(board, 3, -float('inf'), float('inf'), True)  # KI wählt Spalte
            
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)  # Ermittle die unterste freie Zeile
                drop_piece(board, row, col, AI)  # Spielstein setzen
                show_board(board)  # Spielfeld im Terminal anzeigen
                
                # Spielstein physisch zeichnen
                draw_piece(motor_a, motor_b, motor_c,
                           row,
                           col,
                           AI,
                           max_height,
                           min_height,
                           field_width)

                # Überprüfe auf Sieg
                if winning_move(board, AI):
                    print("Spieler O (KI) gewinnt!")
                    game_over = True

        # Spielerwechsel
        turn += 1
        turn %= 2  # Wechsle zwischen 0 und 1

        # Überprüfe auf Unentschieden
        if len(get_valid_locations(board)) == 0:
            print("Unentschieden! Das Spielfeld ist voll.")
            game_over = True

def player_input_via_ev3():
    """
    Ermöglicht dem Spieler die Auswahl einer Spalte über den EV3-Stein.
    
    """
    ev3 = EV3Brick()
    selected_col = 0  # Starte mit der ersten Spalte
    ev3.speaker.beep()  # Signalisiere, dass Eingabe erwartet wird

    # Anzeige der aktuellen Auswahl
    ev3.screen.clear()
    ev3.screen.draw_text(50, 50, "Spalte: " + str(selected_col))

    while True:
        # Überprüfe gedrückte Tasten
        buttons = ev3.buttons.pressed()

        if Button.LEFT in buttons:
            # Nach links bewegen (min. Spalte ist 0)
            selected_col = max(0, selected_col - 1)
            ev3.screen.clear()
            ev3.screen.draw_text(50, 50, "Spalte: " + str(selected_col))
            wait(200)  # Kurze Wartezeit zur Vermeidung von Mehrfacheingaben

        elif Button.RIGHT in buttons:
            # Nach rechts bewegen (max. Spalte ist COLS-1)
            selected_col = min(COLS - 1, selected_col + 1)
            ev3.screen.clear()
            ev3.screen.draw_text(50, 50, "Spalte: " + str(selected_col))
            wait(200)  # Kurze Wartezeit zur Vermeidung von Mehrfacheingaben

        elif Button.CENTER in buttons:
            # Bestätige die Auswahl mit der mittleren Taste
            ev3.screen.clear()
            return selected_col
        
def show_board(board):
    """
    Zeigt das aktuelle Spielfeld im Terminal an.
    
    """
    print("\n")
    # Zeile für Zeile von oben nach unten ausgeben (umgekehrte Reihenfolge)
    for row in reversed(board):
        print('|', end='')
        for cell in row:
            if cell == '🔴' or cell == '🟡':
                print(' ' + cell + ' |', end='')
            else:
                print('   |', end='')  # Drei Leerzeichen für leere Zellen
        print()  # Zeilenumbruch nach jeder Zeile
    
    # Spaltenindizes anzeigen
    print('|', end='')
    for i in range(COLS):
        # Konsistente Formatierung mit einem Leerzeichen vor und nach der Zahl
        print(' ' + str(i+1) + ' |', end='')
    print("\n")

