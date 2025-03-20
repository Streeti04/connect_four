#!/sr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, TouchSensor
from pybricks.parameters import Port
from board_setup import calibrate_board, draw_board
from game_logic import play_game


# Initialisierung der Hardware-Komponenten
ev3 = EV3Brick()  # EV3-Steuereinheit
motor_a = Motor(Port.A)  # Motor A: Hebt und senkt den Stift
motor_b = Motor(Port.B)  # Motor B: Bewegt das Blatt horizontal (X-Achse, invertiert)
motor_c = Motor(Port.C)  # Motor C: Bewegt den Stift vertikal (Y-Achse)
light_sensor = ColorSensor(Port.S3)  # Lichtsensor zur Kantenerkennung
touch_sensor = TouchSensor(Port.S4)  # Berührungssensor für obere Kalibrierungsposition

def main():
    """
Hauptfunktion des Programms.
Steuert den Ablauf:
    1. Signalton zum Programmstart
2. Kalibrierung des Spielfelds
3. Zeichnen des leeren Spielfelds
4. Starten des Spiels
5. Signalton zum Programmende
"""
ev3.speaker.beep()  # Signal, dass das Programm gestartet wurde
# Kalibrierung durchführen und Spielfeldgrenzen ermitteln
max_height, min_height, field_width = calibrate_board(motor_b, motor_c, light_sensor, touch_sensor)
# Leeres Spielfeld zeichnen
draw_board(motor_a, motor_b, motor_c, max_height, min_height, field_width)
# Spiel starten
play_game(motor_a, motor_b, motor_c, max_height, min_height, field_width)
ev3.speaker.beep()  # Signal, dass das Programm beendet wurde
    
if __name__ == "__main__":
    main()
