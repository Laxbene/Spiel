import streamlit as st
import time
from streamlit.components.v1 import html

# --- KONFIGURATION ---
st.set_page_config(page_title="1vs1 Reaction Battle", layout="centered")

# Initialisierung des Spielzustands
if "p1_pos" not in st.session_state:
    st.session_state.update({
        "p1_pos": [2, 2],
        "p2_pos": [7, 7],
        "p1_score": 0,
        "p2_score": 0,
        "p1_cd": 0, # Cooldown Spieler 1
        "p2_cd": 0, # Cooldown Spieler 2
        "game_over": False,
        "last_msg": "Drücke eine Taste zum Starten!"
    })

# --- JAVASCRIPT FÜR TASTATURSTEUERUNG ---
# Dieses Skript sendet Tastendrücke zurück an Streamlit
keystroke_js = """
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    const key = e.key.toLowerCase();
    // Wir senden den Tastendruck als Query-Parameter oder über ein verstecktes Element
    // Einfachste Methode für Streamlit: Ein Event-Trigger
    const streamlitDoc = window.parent.document.querySelector('.stApp');
    if (["w","a","s","d","e","i","j","k","l","o"].includes(key)) {
        window.parent.postMessage({
            type: 'streamlit:set_component_value',
            value: key,
            key: 'keyboard_input'
        }, '*');
    }
});
</script>
"""

# Komponente einbinden (unsichtbar)
st.components.v1.html(keystroke_js, height=0)

# --- SPIELLOGIK ---
def handle_input(key):
    if st.session_state.game_over:
        return

    # Spieler 1 (WASD + E)
    if key == 'w': st.session_state.p1_pos[1] = max(0, st.session_state.p1_pos[1]-1)
    if key == 's': st.session_state.p1_pos[1] = min(9, st.session_state.p1_pos[1]+1)
    if key == 'a': st.session_state.p1_pos[0] = max(0, st.session_state.p1_pos[0]-1)
    if key == 'd': st.session_state.p1_pos[0] = min(9, st.session_state.p1_pos[0]+1)
    
    # Spezialfähigkeit P1 (Teleport zufällig, wenn CD 0)
    if key == 'e' and st.session_state.p1_cd <= 0:
        st.session_state.p1_pos = [st.session_state.p1_pos[0], (st.session_state.p1_pos[1]+3)%10]
        st.session_state.p1_cd = 5
        st.session_state.last_msg = "P1 nutzt TELEPORT!"

    # Spieler 2 (IJKL + O)
    if key == 'i': st.session_state.p2_pos[1] = max(0, st.session_state.p2_pos[1]-1)
    if key == 'k': st.session_state.p2_pos[1] = min(9, st.session_state.p2_pos[1]+1)
    if key == 'j': st.session_state.p2_pos[0] = max(0, st.session_state.p2_pos[0]-1)
    if key == 'l': st.session_state.p2_pos[0] = min(9, st.session_state.p2_pos[0]+1)

    # Spezialfähigkeit P2 (Dash, wenn CD 0)
    if key == 'o' and st.session_state.p2_cd <= 0:
        st.session_state.p2_pos[0] = (st.session_state.p2_pos[0]-3)%10
        st.session_state.p2_cd = 5
        st.session_state.last_msg = "P2 nutzt DASH!"

    # Kollisionsprüfung (Wer auf dem Feld des anderen landet, punktet)
    if st.session_state.p1_pos == st.session_state.p2_pos:
        st.session_state.p1_score += 1
        st.session_state.p1_pos = [0,0]
        st.session_state.p2_pos = [9,9]
        st.session_state.last_msg = "PUNKT FÜR SPIELER 1!"

    # Cooldowns reduzieren
    st.session_state.p1_cd = max(0, st.session_state.p1_cd - 0.5)
    st.session_state.p2_cd = max(0, st.session_state.p2_cd - 0.5)

# --- UI ANZEIGE ---
st.title("⚡ Reaction Battle 1-vs-1")

col1, col2 = st.columns(2)
col1.metric("Spieler 1 (WASD)", f"{st.session_state.p1_score} Pkt", f"CD: {st.session_state.p1_cd}")
col2.metric("Spieler 2 (IJKL)", f"{st.session_state.p2_score} Pkt", f"CD: {st.session_state.p2_cd}")

# Spielfeld zeichnen (10x10 Grid)
grid = [["⬜" for _ in range(10)] for _ in range(10)]
grid[st.session_state.p1_pos[1]][st.session_state.p1_pos[0]] = "🟦" # P1
grid[st.session_state.p2_pos[1]][st.session_state.p2_pos[0]] = "🟥" # P2

display_grid = "\n".join([" ".join(row) for row in grid])
st.code(display_grid, language="text")

st.info(st.session_state.last_msg)

# Reset Button
if st.button("Spiel zurücksetzen"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# Trigger für die Eingabeverarbeitung (Hack um JS-Werte zu fangen)
# In einer echten App würde man hier st_js_blocking nutzen oder ähnliches
query_params = st.query_params
# Da Streamlit Components asynchron sind, nutzen wir hier einen kleinen Trick:
# Wir prüfen, ob eine Eingabe über ein (unsichtbares) Input-Feld reinkommt.
# Für dieses Beispiel nutzen wir ein einfaches Text-Input als Fokus-Fänger.
key_input = st.text_input("Klicke hier, damit Tastatureingaben erkannt werden:", key="manual_input")
if key_input:
    handle_input(key_input[-1].lower())
    # Input leeren für nächsten Zug
    # (In einer High-End-Lösung würde man custom_components nutzen)
