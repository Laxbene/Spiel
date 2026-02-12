import streamlit as st
import time

# Seite konfigurieren
st.set_page_config(page_title="Emoji Clicker", page_icon="🍪")

st.title("🍪 Cookie Clicker Deluxe")

# Spielstand im Session State speichern
if 'cookies' not in st.session_state:
    st.session_state.cookies = 0
if 'auto_clicker' not in st.session_state:
    st.session_state.auto_clicker = 0
if 'multiplier' not in st.session_state:
    st.session_state.multiplier = 1

# --- LOGIK ---

# Kosten für Upgrades
cost_multiplier = 10 * (st.session_state.multiplier ** 2)
cost_auto = 50 + (st.session_state.auto_clicker * 20)

# --- UI LAYOUT ---

col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"Kontostand: {st.session_state.cookies} 🍪")
    
    # Der Haupt-Button
    if st.button("KEKS BACKEN! 🍪", use_container_width=True):
        st.session_state.cookies += 1 * st.session_state.multiplier
        st.rerun()

with col2:
    st.subheader("Shop 🛒")
    
    # Upgrade 1: Stärkerer Klick
    if st.button(f"Stärkerer Klick ({cost_multiplier} 🍪)"):
        if st.session_state.cookies >= cost_multiplier:
            st.session_state.cookies -= cost_multiplier
            st.session_state.multiplier += 1
            st.success("Upgrade gekauft!")
            st.rerun()
        else:
            st.error("Zu wenig Kekse!")

    # Upgrade 2: Auto-Clicker
    if st.button(f"Auto-Backofen ({cost_auto} 🍪)"):
        if st.session_state.cookies >= cost_auto:
            st.session_state.cookies -= cost_auto
            st.session_state.auto_clicker += 1
            st.success("Ofen installiert!")
            st.rerun()
        else:
            st.error("Zu wenig Kekse!")

# Info-Bereich
st.divider()
st.write(f"Klick-Stärke: **{st.session_state.multiplier}** | Automatische Kekse/Sekunde: **{st.session_state.auto_clicker}**")

# Automatisches Backen simulieren
if st.session_state.auto_clicker > 0:
    st.info(f"Deine Öfen backen gerade... {st.session_state.auto_clicker} Kekse pro Sekunde.")
    time.sleep(1) # Kurze Pause
    st.session_state.cookies += st.session_state.auto_clicker
    st.rerun()
