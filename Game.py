import streamlit as st
import random

# Konfiguration der Seite
st.set_page_config(page_title="Streamlit WASD Game", layout="centered")

# Spiel-Einstellungen
GRID_SIZE = 10

# Initialisierung des Spielzustands
if 'player_pos' not in st.session_state:
    st.session_state.player_pos = [0, 0]
    st.session_state.goal_pos = [9, 9]
    st.session_state.score = 0
    st.session_state.message = "Nutze WASD und Enter zum Bewegen!"

def move_player(direction):
    x, y = st.session_state.player_pos
    if direction == 'w' and x > 0: x -= 1
    elif direction == 's' and x < GRID_SIZE - 1: x += 1
    elif direction == 'a' and y > 0: y -= 1
    elif direction == 'd' and y < GRID_SIZE - 1: y += 1
    
    st.session_state.player_pos = [x, y]
    
    # Check ob Ziel erreicht
    if st.session_state.player_pos == st.session_state.goal_pos:
        st.session_state.score += 1
        st.session_state.message = "Gefunden! Neues Ziel generiert."
        st.session_state.goal_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]

# UI Layout
st.title("🕹️ Streamlit Mini-Quest")
st.write(f"**Score:** {st.session_state.score} | {st.session_state.message}")

# Eingabe für Steuerung
control = st.text_input("Steuerung (W/A/S/D eingeben + Enter):", key="input").lower()

if control:
    if control in ['w', 'a', 's', 'd']:
        move_player(control)
    # Input feld leeren (Trick über Session State)
    st.rerun()

# Spielfeld zeichnen
grid = ""
for r in range(GRID_SIZE):
    row_str = ""
    for c in range(GRID_SIZE):
        if [r, c] == st.session_state.player_pos:
            row_str += "🟦 " # Spieler
        elif [r, c] == st.session_state.goal_pos:
            row_str += "🟩 " # Ziel
        else:
            row_str += "⬜ " # Boden
    grid += row_str + "\n\n"

st.markdown(f"```\n{grid}\n```")

# Anleitung
st.info("Klicke in das Textfeld, tippe einen Buchstaben (w, a, s oder d) und drücke Enter.")
