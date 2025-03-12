from pybricks.parameters import Color

# Spielfeld-Konstanten
ROWS = 6  # Anzahl der Zeilen im Spielfeld
COLS = 7  # Anzahl der Spalten im Spielfeld

def calibrate_board(motor_b, motor_c, light_sensor, touch_sensor):
    """
    Kalibriert die Motoren für das Zeichnen des Spielfelds.
    
    Parameter:
        motor_b: Motor für die X-Achse (horizontal)
        motor_c: Motor für die Y-Achse (vertikal)
        light_sensor: Lichtsensor zur Erkennung der Kante
        touch_sensor: Berührungssensor zur Erkennung der oberen Position
        
    Rückgabe:
        max_height: Maximale Höhe (obere Position)
        min_height: Minimale Höhe (untere Position)
        field_width: Breite des Spielfelds
    """
    # Kalibrierung der Y-Achse (Motor C)
    while not touch_sensor.pressed():
        motor_c.run(100)  # Motor läuft nach oben bis der Sensor gedrückt wird
    motor_c.stop()  # Motor stoppen, wenn der Sensor gedrückt wird
    motor_c.reset_angle(0)  # Winkel auf 0 zurücksetzen (Referenzposition)
    motor_c.run_angle(600, -100)  # Ein wenig nach unten fahren
    max_height = motor_c.angle()  # Aktuelle Position als oberen Rand speichern
    min_height = -960  # Unterer Rand (fest definiert)

    # Kalibrierung der X-Achse (Motor B) - Invertiert
    while light_sensor.color() == Color.RED:
        motor_b.run(600)  # Motor läuft, bis der Lichtsensor keine rote Farbe mehr erkennt
    motor_b.stop()  # Motor stoppen
    motor_b.run_angle(600, -200)  # Ein wenig zurückfahren
    motor_b.reset_angle(0)  # Winkel auf 0 zurücksetzen (Referenzposition)
    field_width = 720  # Breite des Spielfelds (fest definiert)

    return max_height, min_height, field_width

def draw_board(motor_a, motor_b, motor_c, max_height, min_height, field_width):
    """
    Zeichnet das Spielfeld mit vertikalen und horizontalen Linien.
    
    Parameter:
        motor_a: Motor für den Stift (heben/senken)
        motor_b: Motor für die X-Achse (horizontal)
        motor_c: Motor für die Y-Achse (vertikal)
        max_height: Maximale Höhe (oberer Rand)
        min_height: Minimale Höhe (unterer Rand)
        field_width: Breite des Spielfelds
    """
    field_height = max_height - min_height  # Berechnung der Spielfeldhöhe

    # Zeichnen der vertikalen Linien
    for i in range(COLS + 1):
        x = i * (field_width / COLS)  # Position der vertikalen Linie berechnen
        motor_b.run_target(600, -x)  # Motor zur X-Position bewegen
        motor_c.run_target(600, max_height)  # Motor zur oberen Position bewegen
        motor_a.run_angle(600, -180)  # Stift absenken
        motor_c.run_target(600, min_height)  # Vertikale Linie nach unten zeichnen
        motor_a.run_angle(600, 180)  # Stift anheben

    # Zeichnen der horizontalen Linien
    motor_b.run_target(600, 0)  # Zurück zur linken Seite
    for i in range(ROWS + 1):
        y = max_height - i * (field_height / ROWS)  # Position der horizontalen Linie berechnen
        motor_c.run_target(600, y)  # Motor zur Y-Position bewegen
        motor_b.run_target(600, 0)  # Links starten
        motor_a.run_angle(600, -180)  # Stift absenken
        motor_b.run_target(600, -field_width)  # Horizontale Linie nach rechts zeichnen
        motor_a.run_angle(600, 180)  # Stift anheben

    # Zurück zur Startposition
    motor_a.run_angle(600, 180)  # Sicherstellen, dass der Stift angehoben ist
    motor_b.run_target(600, 0)  # X-Achse zur Startposition
    motor_c.run_target(600, max_height)  # Y-Achse zur Startposition