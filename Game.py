import streamlit as st
import random
import time
import streamlit.components.v1 as components

# --- INITIALISIERUNG ---
if 'player_hp' not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.boss_hp = 200
    st.session_state.stamina = 50
    st.session_state.rounds = 0
    st.session_state.log = ["Der Kampf beginnt! Weiche den Angriffen im Feld unten aus!"]
    st.session_state.phase = 1

def reset():
    st.session_state.player_hp = 100
    st.session_state.boss_hp = 200
    st.session_state.stamina = 50
    st.session_state.rounds = 0
    st.session_state.log = ["Neuer Versuch! Viel Glück."]
    st.session_state.phase = 1

# --- UI HEADER ---
st.set_page_config(page_title="Action Boss Fight", layout="wide")
st.title("🛡️ Hybrid Boss-Battle: Action & Taktik")

col1, col2 = st.columns(2)

# Dynamische Balken
with col1:
    st.write(f"**Spieler HP: {st.session_state.player_hp}**")
    p_color = "green" if st.session_state.player_hp > 50 else "orange" if st.session_state.player_hp > 20 else "red"
    st.progress(max(0, st.session_state.player_hp) / 100)
    st.write(f"Ausdauer: {st.session_state.stamina}")

with col2:
    boss_label = "BOSS" if st.session_state.phase == 1 else "🔥 BOSS WÜTEND"
    st.write(f"**{boss_label} HP: {st.session_state.boss_hp}**")
    st.progress(max(0, st.session_state.boss_hp) / 200)

# --- PHASEN-LOGIK ---
if st.session_state.boss_hp < 80 and st.session_state.phase == 1:
    st.session_state.phase = 2
    st.error("PHASE 2: Der Boss beschwört einen Feuersturm!")

# --- ACTION KOMPONENTE (JavaScript 2D Ausweichen) ---
st.subheader("🕹️ Ausweich-Arena (Nutze die MAUS zum Ausweichen)")
# Kleines JS-Spiel: Wenn der Spieler den roten Kreis berührt, verliert er HP
action_game_html = """
<div id="game-container" style="border: 2px solid #555; background: #111; width: 100%; height: 200px; position: relative; overflow: hidden; cursor: crosshair;">
    <div id="player" style="width: 20px; height: 20px; background: #00f; position: absolute; border-radius: 50%;"></div>
    <div id="enemy" style="width: 30px; height: 30px; background: #f00; position: absolute; border-radius: 50%; top: 0; left: 50%;"></div>
</div>
<script>
    const container = document.getElementById('game-container');
    const player = document.getElementById('player');
    const enemy = document.getElementById('enemy');
    let enemyX = 50; let enemyY = 0; let speed = 3;

    container.onmousemove = (e) => {
        const rect = container.getBoundingClientRect();
        player.style.left = (e.clientX - rect.left - 10) + 'px';
        player.style.top = (e.clientY - rect.top - 10) + 'px';
    };

    setInterval(() => {
        enemyY += speed;
        if(enemyY > 200) { enemyY = 0; enemyX = Math.random() * 90; }
        enemy.style.top = enemyY + 'px';
        enemy.style.left = enemyX + '%';
        
        // Einfache Kollisionsabfrage
        const p = player.getBoundingClientRect();
        const e = enemy.getBoundingClientRect();
        if(!(p.right < e.left || p.left > e.right || p.bottom < e.top || p.top > e.bottom)) {
            container.style.background = "#400";
            setTimeout(() => { container.style.background = "#111"; }, 100);
        }
    }, 20);
</script>
"""
components.html(action_game_html, height=220)

# --- KAMPFSYSTEM ---
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("⚔️ Nahkampf", use_container_width=True):
        if st.session_state.stamina >= 10:
            dmg = random.randint(15, 30)
            st.session_state.boss_hp -= dmg
            st.session_state.stamina -= 10
            st.session_state.rounds += 1
            st.session_state.log.insert(0, f"Runde {st.session_state.rounds}: Treffer für {dmg} Schaden!")
            # Boss schlägt zurück
            boss_dmg = random.randint(10, 20) if st.session_state.phase == 1 else random.randint(20, 35)
            st.session_state.player_hp -= boss_dmg
            st.rerun()

with c2:
    if st.button("🛡️ Blocken", use_container_width=True):
        st.session_state.stamina += 5
        st.session_state.player_hp -= 5
        st.session_state.log.insert(0, "Du blockst! Minimaler Schaden genommen.")
        st.rerun()

with c3:
    if st.button("🧘 Verschnaufen", use_container_width=True):
        st.session_state.stamina += 30
        st.session_state.log.insert(0, "Du regenerierst Ausdauer.")
        st.rerun()

# --- LOG & ENDE ---
st.divider()
log_col, board_col = st.columns([2, 1])

with log_col:
    st.write("📜 Kampf-Log")
    st.container(height=150).write("\n".join(st.session_state.log))

if st.session_state.boss_hp <= 0:
    st.balloons()
    st.success(f"SIEG in {st.session_state.rounds} Runden!")
    loot = random.choice(["Drachentöter-Axt", "Schild der Hoffnung", "Glänzender Stein"])
    st.info(f"Beute: {loot}")
    if st.button("Neustart"): reset()
    st.stop()

if st.session_state.player_hp <= 0:
    st.error("Du wurdest besiegt!")
    if st.button("Erneut versuchen"): reset()
    st.stop()
