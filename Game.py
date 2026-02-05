import streamlit as st
import random
import time

# --- INITIALISIERUNG ---
if 'game_over' not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.player_stamina = 50
    st.session_state.boss_hp = 200
    st.session_state.boss_max_hp = 200
    st.session_state.log = ["Der Kampf beginnt! Der 'Eisengolem' starrt dich an."]
    st.session_state.rounds = 0
    st.session_state.phase = 1
    st.session_state.game_over = False
    st.session_state.leaderboard = []

def add_log(text):
    st.session_state.log.insert(0, f"Runde {st.session_state.rounds}: {text}")

def reset_game():
    st.session_state.player_hp = 100
    st.session_state.player_stamina = 50
    st.session_state.boss_hp = 200
    st.session_state.phase = 1
    st.session_state.rounds = 0
    st.session_state.log = ["Ein neuer Herausforderer tritt vor!"]
    st.session_state.game_over = False

# --- LOGIK ---
def boss_turn():
    if st.session_state.boss_hp <= 0:
        return

    damage = random.randint(10, 18) if st.session_state.phase == 1 else random.randint(18, 30)
    
    # Boss Spezialattacken in Phase 2
    if st.session_state.phase == 2 and random.random() > 0.7:
        damage += 15
        add_log("🔥 BOSS-SPEZIAL: 'Inferno-Schlag' trifft dich hart!")
    else:
        add_log(f"⚔️ Der Boss greift an und verursacht {damage} Schaden.")
    
    st.session_state.player_hp -= damage

# --- UI LAYOUT ---
st.set_page_config(page_title="Boss Fight: The Golem", layout="centered")
st.title("⚔️ Boss Fight: Streamlit Edition")

# Fortschrittsbalken mit Farbumschlag
def get_hp_color(current, max_val):
    ratio = current / max_val
    if ratio > 0.6: return "green"
    if ratio > 0.3: return "orange"
    return "red"

col1, col2 = st.columns(2)

with col1:
    st.subheader("Spieler")
    p_color = get_hp_color(st.session_state.player_hp, 100)
    st.progress(max(0, st.session_state.player_hp) / 100)
    st.write(f"HP: {max(0, st.session_state.player_hp)} / 100")
    st.write(f"Ausdauer: {st.session_state.player_stamina}")

with col2:
    phase_label = "PHASE 1" if st.session_state.phase == 1 else "🔥 PHASE 2: WÜTEND"
    st.subheader(f"Boss ({phase_label})")
    b_color = get_hp_color(st.session_state.boss_hp, st.session_state.boss_max_hp)
    st.progress(max(0, st.session_state.boss_hp) / st.session_state.boss_max_hp)
    st.write(f"Boss HP: {max(0, st.session_state.boss_hp)} / {st.session_state.boss_max_hp}")

# Phasen-Check
if st.session_state.boss_hp < (st.session_state.boss_max_hp * 0.4) and st.session_state.phase == 1:
    st.session_state.phase = 2
    st.warning("ACHTUNG: Der Boss wird wütend! Phase 2 beginnt!")
    add_log("📢 SYSTEM: Der Boss ist in Phase 2 eingetreten!")

st.divider()

# --- AKTIONEN ---
if not st.session_state.game_over:
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("Nahkampf (15 Stamina)", use_container_width=True):
            if st.session_state.player_stamina >= 15:
                dmg = random.randint(15, 35)
                st.session_state.boss_hp -= dmg
                st.session_state.player_stamina -= 15
                st.session_state.rounds += 1
                add_log(f"🤺 Du triffst für {dmg} Schaden!")
                boss_turn()
            else:
                st.error("Zu müde!")

    with c2:
        if st.button("Blocken (Schild)", use_container_width=True):
            st.session_state.rounds += 1
            add_log("🛡️ Du gehst in Verteidigungshaltung (Schaden reduziert).")
            # Reduzierter Boss-Schaden Logik hier vereinfacht
            st.session_state.player_hp -= random.randint(2, 5)
            st.session_state.player_stamina += 5
            boss_turn()

    with c3:
        if st.button("Verschnaufen", use_container_width=True):
            st.session_state.rounds += 1
            st.session_state.player_stamina += 30
            add_log("🧘 Du atmest tief durch und regenerierst Ausdauer.")
            boss_turn()

# --- SPIELENDE ---
if st.session_state.player_hp <= 0:
    st.error("Du bist gefallen... GAME OVER.")
    st.session_state.game_over = True
    if st.button("Erneut versuchen"): reset_game()

elif st.session_state.boss_hp <= 0:
    st.balloons()
    st.success(f"SIEG! Du hast den Boss in {st.session_state.rounds} Runden besiegt.")
    
    # Loot Generator
    loot = random.choice(["Goldschwert", "Drachenschuppe", "Alter Schuh", "Magischer Ring"])
    st.info(f"🎁 Du hast gefunden: {loot}")
    
    # Bestenliste Logik
    if not st.session_state.game_over:
        st.session_state.leaderboard.append(st.session_state.rounds)
        st.session_state.game_over = True

    st.subheader("🏆 Bestenliste (Runden)")
    sorted_scores = sorted(st.session_state.leaderboard)
    st.table({"Rang": range(1, len(sorted_scores)+1), "Runden": sorted_scores})
    
    if st.button("Nächster Boss"): reset_game()

# --- KAMPF-LOG ---
st.subheader("Kampf-Log")
with st.container(border=True):
    # Simulation eines scrollbaren Bereichs mit fester Höhe
    log_text = "\n".join(st.session_state.log)
    st.text_area(label="Events", value=log_text, height=200, disabled=True, label_visibility="collapsed")

if st.sidebar.button("Reset Game"):
    reset_game()
    st.rerun()
