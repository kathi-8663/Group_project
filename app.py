import streamlit as st
import json
import os

# --- DATENBANK FUNKTIONEN ---
DB_FILE = "users_db.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    if username in users:
        return False
    # Wir speichern direkt ein Profil-Objekt für neue User mit
    users[username] = {
        "password": password,
        "level": 1,
        "xp": 0,
        "badges": [],
        "current_challenges": [],
        "completed_challenges": []
    }
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)
    return True

# --- APP SETUP ---
st.set_page_config(page_title="GroupQuest Profil", page_icon="🏆")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN / REGISTRIERUNG ---
if not st.session_state.logged_in:
    st.title("🏆 GroupQuest")
    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])
    
    with tab1:
        u_name = st.text_input("Username")
        u_pw = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            users = load_users()
            # Prüfen ob User da ist und Passwort (im Feld 'password') stimmt
            if u_name in users and users[u_name]["password"] == u_pw:
                st.session_state.logged_in = True
                st.session_state.username = u_name
                st.rerun()
            else:
                st.error("Login fehlgeschlagen.")

    with tab2:
        new_u = st.text_input("Wähle Usernamen")
        new_p = st.text_input("Wähle Passwort", type="password")
        if st.button("Jetzt registrieren"):
            if save_user(new_u, new_p):
                st.success("Erfolgreich! Bitte logge dich jetzt ein.")
            else:
                st.error("User existiert bereits.")

# --- EINGELOGGTES PROFIL ---
else:
    # Daten laden
    all_users = load_users()
    user_data = all_users[st.session_state.username]

    # Sidebar für Logout
    st.sidebar.title(f"@{st.session_state.username}")
    if st.sidebar.button("Abmelden"):
        st.session_state.logged_in = False
        st.rerun()

    # Profil Header
    st.title(f"Profil von {st.session_state.username}")
    
    # 1. Metriken: Level und XP
    col1, col2 = st.columns(2)
    col1.metric("Aktuelles Level", f"Lvl {user_data['level']}")
    col2.metric("Erfahrungspunkte (XP)", f"{user_data['xp']} XP")
    
    st.divider()

    # 2. Badges (Erfolge)
    st.subheader("🛡️ Deine Badges")
    if user_data['badges']:
        # Zeige Badges nebeneinander an
        badge_cols = st.columns(len(user_data['badges']))
        for i, badge in enumerate(user_data['badges']):
            badge_cols[i].info(f"🏅 {badge}")
    else:
        st.write("Noch keine Badges verdient. Bleib dran!")

    st.divider()

    # 3. Challenges (Aktuell vs. Erfüllt)
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("🔥 Aktuelle Quests")
        if user_data['current_challenges']:
            for quest in user_data['current_challenges']:
                st.checkbox(quest, value=False, key=quest)
        else:
            st.info("Keine aktiven Challenges.")
            if st.button("Finde neue Challenges"):
                st.write("Suche läuft...")

    with right_col:
        st.subheader("✅ Erfüllte Challenges")
        if user_data['completed_challenges']:
            for comp in user_data['completed_challenges']:
                st.success(f"Erledigt: {comp}")
        else:
            st.write("Du hast noch keine Challenge abgeschlossen.")

# --- STYLE ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 40px;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)
