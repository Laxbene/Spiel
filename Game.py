import streamlit as st
import streamlit.components.v1 as components
import time
import random

# --- KONFIGURATION ---
ST_FPS = 30  # Bilder pro Sekunde
GAME_WIDTH = 600
GAME_HEIGHT = 400
PLAYER_SIZE = 20
MOVE_SPEED = 10

# --- SEITEN-SETUP ---
st.set_page_config(page_title="1-vs-1 Reaction Arena", layout="centered")
st.title("⚡ 1-vs-1 Reaction Arena")
st.write("Spieler 1: WASD + E | Spieler 2: IJKL + O")

# --- JAVASCRIPT FÜR TASTATUR-STEUERUNG ---
# Dieses Skript fängt Tastendrücke ab und sendet sie an Streamlit zurück
keystroke_js = """
<script>
    const pressedKeys = new Set();
    document.addEventListener('keydown', (e) => {
        pressedKeys.add(e.key.toLowerCase());
        sendToStreamlit();
    });
    document.addEventListener('keyup', (e) => {
        pressedKeys.delete(e.key.toLowerCase());
        sendToStreamlit();
    });

    function sendToStreamlit() {
        const keyArray = Array.from(pressedKeys);
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: keyArray
        }, '*');
    }
</script>
"""

# Komponente zum Empfangen der Tasten (unsichtbar)
def key_receiver():
    return components.html(keystroke_js, height=0, width=0)

# --- SPIELZUSTAND INITIALISIEREN ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'p1': {'x': 100, 'y': 200, 'score': 0, 'cd': 0},
        'p2': {'x': 500, 'y': 200, 'score': 0, 'cd': 0},
        'target': {'x': 300, 'y': 200},
        'active': True,
        'timer': 30.0
    }

gs = st.session_state.game_state

# --- LOGIK-FUNKTIONEN ---
def update_game(keys):
    if not gs['active']: return

    # Steuerung Spieler 1 (WASD)
    if 'w' in keys and gs['p1']['y'] > 0: gs['p1']['y'] -= MOVE_SPEED
    if 's' in keys and gs['p1']['y'] < GAME_HEIGHT - PLAYER_SIZE: gs['p1']['y'] += MOVE_SPEED
    if 'a' in keys and gs['p1']['x'] > 0: gs['p1']['x'] -= MOVE_SPEED
    if 'd' in keys and gs['p1']['x'] < GAME_WIDTH - PLAYER_SIZE: gs['p1']['x'] += MOVE_SPEED

    # Steuerung Spieler 2 (IJKL)
    if 'i' in keys and gs['p2']['y'] > 0: gs['p2']['y'] -= MOVE_SPEED
    if 'k' in keys and gs['p2']['y'] < GAME_HEIGHT - PLAYER_SIZE: gs['p2']['y'] += MOVE_SPEED
    if 'j' in keys and gs['p2']['x'] > 0: gs['p2']['x'] -= MOVE_SPEED
    if 'l' in keys and gs['p2']['x'] < GAME_WIDTH - PLAYER_SIZE: gs['p2']['x'] += MOVE_SPEED

    # Spezialfähigkeiten (Teleport zum Ziel bei E / O)
    for p_key, skill_key in [('p1', 'e'), ('p2', 'o')]:
        if skill_key in keys and gs[p_key]['cd'] <= 0:
            gs[p_key]['x'] = gs['target']['x'] + (random.randint(-20, 20))
            gs[p_key]['y'] = gs['target']['y'] + (random.randint(-20, 20))
            gs[p_key]['cd'] = 50 # Cooldown Frames

    # Cooldowns verringern
    if gs['p1']['cd'] > 0: gs['p1']['cd'] -= 1
    if gs['p2']['cd'] > 0: gs['p2']['cd'] -= 1

    # Kollision mit Ziel (Punktesammeln)
    for p in ['p1', 'p2']:
        if abs(gs[p]['x'] - gs['target']['x']) < 20 and abs(gs[p]['y'] - gs['target']['y']) < 20:
            gs[p]['score'] += 1
            gs['target']['x'] = random.randint(50, GAME_WIDTH - 50)
            gs['target']['y'] = random.randint(50, GAME_HEIGHT - 50)

# --- UI RENDERING ---
active_keys = key_receiver() 
# Hinweis: In einer echten App würde man hier eine stabilere Custom Component nutzen.
# Für diesen Prototyp nutzen wir einen Workaround mit Session State.

visuals = st.empty()

# --- GAME LOOP ---
def run_loop():
    start_time = time.time()
    while gs['active']:
        # Zeit berechnen
        elapsed = time.time() - start_time
        gs['timer'] = max(0, 30 - elapsed)
        
        if gs['timer'] <= 0:
            gs['active'] = False
        
        # Hier müssten normalerweise die Tasten verarbeitet werden. 
        # Da Streamlit bei jedem Key-Event das Skript neu ausführt,
        # nutzen wir das aus:
        update_game(st.session_state.get('keys', []))
        
        # Zeichne das Spielfeld als SVG (einfach und schnell)
        svg_ui = f"""
        <svg width="{GAME_WIDTH}" height="{GAME_HEIGHT}" style="background-color: #1e1e1e; border: 2px solid #555;">
            <circle cx="{gs['target']['x']}" cy="{gs['target']['y']}" r="10" fill="yellow" />
            <rect x="{gs['p1']['x']}" y="{gs['p1']['y']}" width="{PLAYER_SIZE}" height="{PLAYER_SIZE}" fill="#FF4B4B" />
            <text x="{gs['p1']['x']}" y="{gs['p1']['y']-5}" fill="white" font-size="12">P1 (CD: {gs['p1']['cd']})</text>
            <rect x="{gs['p2']['x']}" y="{gs['p2']['y']}" width="{PLAYER_SIZE}" height="{PLAYER_SIZE}" fill="#0068C9" />
            <text x="{gs['p2']['x']}" y="{gs['p2']['y']-5}" fill="white" font-size="12">P2 (CD: {gs['p2']['cd']})</text>
        </svg>
        """
        
        with visuals.container():
            cols = st.columns(3)
            cols[0].metric("Spieler 1", gs['p1']['score'])
            cols[1].metric("Zeit", round(gs['timer'], 1))
            cols[2].metric("Spieler 2", gs['p2']['score'])
            st.write(svg_ui, unsafe_allow_html=True)
            
        time.sleep(1/ST_FPS)
        if not gs['active']:
            winner = "Spieler 1" if gs['p1']['score'] > gs['p2']['score'] else "Spieler 2"
            if gs['p1']['score'] == gs['p2']['score']: winner = "Unentschieden"
            st.balloons()
            st.header(f"🏆 Gewinner: {winner}!")
            if st.button("Neustart"):
                del st.session_state.game_state
                st.rerun()
            break

# Start des Loops
run_loop()
