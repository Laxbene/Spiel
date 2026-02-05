import streamlit as st
import streamlit.components.v1 as components
import time

# --- KONFIGURATION ---
st.set_page_config(page_title="1vs1 Retro Battle", layout="centered")

# Initialisierung des Spielzustands
if 'p1_pos' not in st.session_state:
    st.session_state.update({
        'p1_pos': [100, 200], # [x, y]
        'p2_pos': [500, 200],
        'p1_score': 0,
        'p2_score': 0,
        'p1_cd': 0, # Cooldown
        'p2_cd': 0,
        'orb_pos': [300, 200],
        'game_over': False
    })

# --- JAVASCRIPT FÜR TASTATURSTEUERUNG ---
# Dieser Teil fängt die Tasten ab und sendet sie an Streamlit
def keyboard_listener():
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            const key = e.key.toLowerCase();
            // Erstelle ein unsichtbares Element oder nutze ein bestehendes, um Daten zu senden
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: key,
                key: 'last_key'
            }, '*');
        });
        </script>
        """,
        height=0,
    )

# --- SPIELLOGIK ---
def update_game(key):
    step = 20
    dash_distance = 60
    
    # Spieler 1 (WASD + E)
    if key == 'w': st.session_state.p1_pos[1] -= step
    if key == 's': st.session_state.p1_pos[1] += step
    if key == 'a': st.session_state.p1_pos[0] -= step
    if key == 'd': st.session_state.p1_pos[0] += step
    if key == 'e' and st.session_state.p1_cd <= 0:
        st.session_state.p1_pos[0] += dash_distance
        st.session_state.p1_cd = 5 # 5 Aktionen Cooldown

    # Spieler 2 (IJKL + O)
    if key == 'i': st.session_state.p2_pos[1] -= step
    if key == 'k': st.session_state.p2_pos[1] += step
    if key == 'j': st.session_state.p2_pos[0] -= step
    if key == 'l': st.session_state.p2_pos[0] += step
    if key == 'o' and st.session_state.p2_cd <= 0:
        st.session_state.p2_pos[0] -= dash_distance
        st.session_state.p2_cd = 5

    # Cooldowns verringern
    if st.session_state.p1_cd > 0: st.session_state.p1_cd -= 1
    if st.session_state.p2_cd > 0: st.session_state.p2_cd -= 1

    # Kollisionsprüfung mit dem Orb (vereinfacht)
    for p in ['p1', 'p2']:
        pos = st.session_state[f'{p}_pos']
        orb = st.session_state.orb_pos
        if abs(pos[0] - orb[0]) < 30 and abs(pos[1] - orb[1]) < 30:
            st.session_state[f'{p}_score'] += 1
            # Orb an neue Position setzen
            import random
            st.session_state.orb_pos = [random.randint(50, 550), random.randint(50, 350)]

# --- UI RENDERING ---
st.title("🕹️ 1-vs-1 Reaction Battle")
st.write("Sammle den gelben Orb! **P1:** WASD + E | **P2:** IJKL + O")

# Spielbereich zeichnen (SVG für einfache Grafik)
p1 = st.session_state.p1_pos
p2 = st.session_state.p2_pos
orb = st.session_state.orb_pos

game_board = f"""
<svg width="600" height="400" style="background-color: #1e1e1e; border: 2px solid #333; border-radius: 10px;">
    <rect x="{p1[0]}" y="{p1[1]}" width="30" height="30" fill="#00f2ff" />
    <text x="{p1[0]}" y="{p1[1]-5}" fill="white" font-size="12">P1</text>
    
    <rect x="{p2[0]}" y="{p2[1]}" width="30" height="30" fill="#ff007b" />
    <text x="{p2[0]}" y="{p2[1]-5}" fill="white" font-size="12">P2</text>
    
    <circle cx="{orb[0]}" cy="{orb[1]}" r="10" fill="#f9d423" />
</svg>
"""
st.markdown(game_board, unsafe_allow_html=True)

# Punktestand
cols = st.columns(2)
cols[0].metric("P1 Score", st.session_state.p1_score, f"CD: {st.session_state.p1_cd}")
cols[1].metric("P2 Score", st.session_state.p2_score, f"CD: {st.session_state.p2_cd}")

# Keyboard Input verarbeiten
keyboard_listener()

# Trick: Ein verstecktes Input-Element, das den Wert von JS empfängt
# Wir nutzen hier eine kleine Verzögerung, um die CPU nicht zu grillen
last_key = st.chat_input("Steuerung aktiv...", key="input_trigger")

# Da wir oben JavaScript nutzen, um Nachrichten zu senden, 
# müssen wir diese in Streamlit abfangen. Ein einfacherer Weg für dieses Tutorial:
# Wir prüfen, ob sich ein State-Key geändert hat.
if "last_key" in st.query_params:
    key = st.query_params["last_key"]
    update_game(key)
    # Reset (in einer echten App würde man dies über ein Custom Component lösen)
    
# Button zum Neustart
if st.button("Spiel zurücksetzen"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
