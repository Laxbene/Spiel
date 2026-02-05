import streamlit as st
import streamlit.components.v1 as components
import time

# --- KONFIGURATION ---
st.set_page_config(page_title="1vs1 Streamlit Battle", layout="centered")

# Initialisierung des Spielzustands
if 'p1_pos' not in st.session_state:
    st.session_state.update({
        'p1_pos': [20, 50], # [x, y] in Prozent
        'p2_pos': [80, 50],
        'p1_score': 0,
        'p2_score': 0,
        'p1_cd': 0, # Cooldown Zeitstempel
        'p2_cd': 0,
        'last_update': time.time()
    })

# --- JAVASCRIPT FÜR TASTATUR ---
# Dieses Skript fängt Tasten ab und sendet sie an Streamlit zurück
keystroke_js = """
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    const key = e.key.toLowerCase();
    // Wir senden die Taste an ein verstecktes Streamlit-Input-Feld oder nutzen die API
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: key,
    }, '*');
});
</script>
"""
components.html(keystroke_js, height=0)

# Ein kleiner Workaround: Wir nutzen ein Text-Input, das durch JS gefüllt wird
# Aber für die Einfachheit nutzen wir hier die direkte Steuerung via Buttons + State
# In einer echten Streamlit Game Engine würde man "streamlit-gamepad" o.ä. nutzen.

## SPIEL-LOGIK FUNKTIONEN
def move_player(player, direction):
    step = 5
    if player == 1:
        pos = st.session_state.p1_pos
    else:
        pos = st.session_state.p2_pos
        
    if direction == 'w' or direction == 'i': pos[1] = max(0, pos[1] - step)
    if direction == 's' or direction == 'k': pos[1] = min(100, pos[1] + step)
    if direction == 'a' or direction == 'j': pos[0] = max(0, pos[0] - step)
    if direction == 'd' or direction == 'l': pos[0] = min(100, pos[0] + step)

def check_collision():
    p1 = st.session_state.p1_pos
    p2 = st.session_state.p2_pos
    dist = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
    if dist < 8: # Kollisionsradius
        return True
    return False

# --- UI LAYOUT ---
st.title("⚡ Streamlit React Battle ⚡")
cols = st.columns(2)
cols[0].metric("Spieler 1 (WASD + E)", st.session_state.p1_score)
cols[1].metric("Spieler 2 (IJKL + O)", st.session_state.p2_score)

# Spielfeld Visualisierung (CSS-basiert)
game_field = st.empty()

def draw_game():
    p1 = st.session_state.p1_pos
    p2 = st.session_state.p2_pos
    html_code = f"""
    <div style="position: relative; width: 100%; height: 400px; background-color: #1e1e1e; border-radius: 10px; border: 2px solid #444;">
        <div style="position: absolute; left: {p1[0]}%; top: {p1[1]}%; width: 30px; height: 30px; background: #FF4B4B; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 15px #FF4B4B;"></div>
        <div style="position: absolute; left: {p2[0]}%; top: {p2[1]}%; width: 30px; height: 30px; background: #0068C9; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 15px #0068C9;"></div>
    </div>
    """
    game_field.markdown(html_code, unsafe_allow_html=True)

draw_game()

# --- INPUT HANDLING ---
# Da Streamlit auf Events wartet, nutzen wir hier ein Eingabefeld für die Demo-Steuerung
# Für echtes "Simultan-Gaming" müsste man auf eine Custom Component wie 'streamlit-keyboard-event' setzen.
cmd = st.chat_input("Drücke Tasten hier (Fokus-Hack) oder nutze Buttons:")

if cmd:
    cmd = cmd.lower()
    # P1 Controls
    if cmd in ['w', 'a', 's', 'd']: move_player(1, cmd)
    if cmd == 'e': 
        st.session_state.p1_pos[0] += 20 # Teleport Dash
        st.toast("P1 Dash!")
        
    # P2 Controls
    if cmd in ['i', 'j', 'k', 'l']: move_player(2, cmd)
    if cmd == 'o': 
        st.session_state.p2_pos[0] -= 20 # Teleport Dash
        st.toast("P2 Dash!")

    if check_collision():
        st.session_state.p1_score += 1
        st.balloons()
        st.session_state.p1_pos = [20, 50]
        st.session_state.p2_pos = [80, 50]
    
    st.rerun()

st.info("💡 **Tipp:** Da Streamlit kein klassisches Game-Engine-Looping hat, klicke in das Chat-Feld unten und gib die Taste ein. Für echtes 'Simultan-Feeling' am selben Gerät ist das Web-Interface von Streamlit ohne Custom Components limitiert.")
