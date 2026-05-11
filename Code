import streamlit as st
import json
import os
import random
import string
import base64
from datetime import datetime

# --- DATEI-PFADE ---
DB_FILE = "users_db.json"
CHALLENGE_FILE = "challenges_db.json"
POSTS_FILE = "posts_db.json"

# --- HELFER FUNKTIONEN ---
def load_json(file):
    if not os.path.exists(file): return {} if "users" in file else []
    with open(file, "r") as f:
        try: return json.load(f)
        except: return {} if "users" in file else []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def get_image_base64(file):
    return base64.b64encode(file.getvalue()).decode()

# --- APP SETUP ---
st.set_page_config(page_title="GroupQuest", page_icon="🏆", layout="centered")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- LOGIN / REGISTRIERUNG ---
if not st.session_state.logged_in:
    st.title("🏆 GroupQuest")
    t1, t2 = st.tabs(["Anmelden", "Registrieren"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Passwort", type="password", key="l_p")
        if st.button("Einloggen"):
            users = load_json(DB_FILE)
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Falscher User oder Passwort.")
    with t2:
        nu = st.text_input("Name", key="r_u")
        np = st.text_input("Passwort", type="password", key="r_p")
        if st.button("Registrieren"):
            users = load_json(DB_FILE)
            if nu and nu not in users:
                users[nu] = {"password": np, "level": 1, "xp": 0, "current_challenges": []}
                save_json(DB_FILE, users)
                st.success("Erfolgreich registriert!")
            else: st.error("Name vergeben.")

# --- HAUPTBEREICH ---
else:
    all_users = load_json(DB_FILE)
    user_data = all_users.get(st.session_state.username, {})

    if st.session_state.page == "Home":
        st.title(f"Moin, {st.session_state.username}! 👋")
        st.write("Bereit für die nächste Herausforderung? Schau unter **Explore** nach.")
        
        # Kurze Status-Übersicht auf Home
        xp = user_data.get("xp", 0)
        level = (xp // 100) + 1
        st.metric("Dein aktuelles Level", f"Lvl {level}")

    elif st.session_state.page == "Entdecken":
        st.title("🔍 Challenges")
        t_pub, t_join, t_create = st.tabs(["🔥 Öffentliche", "🔑 Code", "➕ Erstellen"])
        
        challenges = load_json(CHALLENGE_FILE)
        posts = load_json(POSTS_FILE)

        with t_pub:
            search = st.text_input("🔍 Challenges durchsuchen...", placeholder="Name oder Kategorie")
            st.markdown("---")
            
            # Filter: Nur Öffentlich & Suchbegriff
            filtered = [c for c in challenges if c.get("visibility") == "Öffentlich" and 
                        (search.lower() in c['title'].lower() or search.lower() in c['category'].lower())]
            
            if not filtered:
                st.info("Keine öffentlichen Challenges gefunden.")
            
            for c in filtered:
                is_owner = c.get("owner") == st.session_state.username
                is_member = c['code'] in user_data.get("current_challenges", [])
                
                with st.expander(f"{c['category']}: {c['title']} {'⭐ (Owner)' if is_owner else ''}"):
                    st.write(f"**Dauer:** {c.get('duration', 'k.A.')}")
                    st.write(f"**Beschreibung:** {c.get('description', '-')}")
                    st.write(f"**Regeln:** {c.get('rules', '-')}")
                    
                    if not is_member and not is_owner:
                        if st.button("Teilnehmen", key=f"pub_{c['code']}"):
                            all_users[st.session_state.username]["current_challenges"].append(c['code'])
                            save_json(DB_FILE, all_users)
                            st.rerun()
                    
                    if is_member or is_owner:
                        st.divider()
                        if is_member:
                            st.markdown("#### 📸 Beweis einreichen")
                            with st.form(key=f"f_{c['code']}", clear_on_submit=True):
                                img = st.file_uploader("Foto hochladen", type=["jpg", "png"])
                                txt = st.text_input("Kommentar")
                                if st.form_submit_button("Posten") and img:
                                    posts.append({
                                        "id": "".join(random.choices(string.digits, k=10)),
                                        "challenge_code": c['code'],
                                        "user": st.session_state.username,
                                        "image": get_image_base64(img),
                                        "text": txt,
                                        "confirmed": False,
                                        "date": datetime.now().strftime("%d.%m. | %H:%M")
                                    })
                                    save_json(POSTS_FILE, posts)
                                    st.success("Hochgeladen!")
                                    st.rerun()

                        st.write("#### 💬 Community Feed")
                        c_posts = [p for p in posts if p['challenge_code'] == c['code']]
                        for p in reversed(c_posts):
                            st.write(f"**{p['user']}** ({p.get('date', '')})")
                            st.image(f"data:image/png;base64,{p['image']}", use_container_width=True)
                            if p.get('text'): st.write(f"» {p['text']}")
                            
                            if is_owner and not p.get('confirmed'):
                                if st.button(f"✅ Bestätigen", key=f"c_{p['id']}"):
                                    p['confirmed'] = True
                                    all_users[p['user']]["xp"] += 50
                                    save_json(POSTS_FILE, posts)
                                    save_json(DB_FILE, all_users)
                                    st.rerun()
                            elif p.get('confirmed'):
                                st.success("Vom Ersteller bestätigt! 🏆")
                            st.divider()

        with t_join:
            st.subheader("Privater Challenge beitreten")
            p_code = st.text_input("Code eingeben (GQ-XXXXX)")
            if st.button("Code prüfen"):
                target = next((c for c in challenges if c["code"] == p_code), None)
                if target:
                    if p_code not in user_data["current_challenges"]:
                        all_users[st.session_state.username]["current_challenges"].append(p_code)
                        save_json(DB_FILE, all_users)
                        st.success(f"Erfolg! Du bist nun Teil von: {target['title']}")
                        st.rerun()
                    else: st.info("Du bist bereits in dieser Challenge.")
                else: st.error("Ungültiger Code.")

        with t_create:
            with st.form("new_quest"):
                st.subheader("Erstelle dein eigenes Event")
                name = st.text_input("Name der Challenge")
                cat = st.selectbox("Kategorie", ["Sport", "Mindset", "Ernährung", "Produktivität", "Hobby"])
                dur = st.text_input("Dauer (z.B. 14 Tage)")
                desc = st.text_area("Beschreibung")
                rules = st.text_area("Regeln für den Beweis")
                vis = st.radio("Sichtbarkeit", ["Öffentlich", "Privat"])
                
                if st.form_submit_button("Quest erstellen"):
                    if name:
                        code = "GQ-" + "".join(random.choices(string.ascii_uppercase, k=5))
                        new_c = {
                            "title": name, "category": cat, "duration": dur,
                            "description": desc, "rules": rules, "visibility": vis,
                            "code": code, "owner": st.session_state.username
                        }
                        challenges.append(new_c)
                        save_json(CHALLENGE_FILE, challenges)
                        st.success(f"Challenge erstellt! Code: {code}")
                    else: st.error("Der Name darf nicht leer sein.")

    elif st.session_state.page == "Profil":
        st.title("👤 Dein Profil")
        st.subheader(st.session_state.username)
        
        # --- LEVEL & PROGRESS LOGIK ---
        xp = user_data.get("xp", 0)
        level = (xp // 100) + 1
        xp_in_level = xp % 100
        progress = xp_in_level / 100.0
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Level", level)
        with col2:
            st.write(f"**XP bis Level-Up:** {xp_in_level} / 100")
            st.progress(progress)
            
        st.write(f"Gesammelte Erfahrung insgesamt: **{xp} XP**")
        st.divider()
        
        if st.button("Abmelden", type="primary"):
            st.session_state.logged_in = False
            st.rerun()

    # --- STICKY NAVBAR ---
    st.divider()
    n1, n2, n3 = st.columns(3)
    if n1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
    if n2.button("🔍 Explore"): st.session_state.page = "Entdecken"; st.rerun()
    if n3.button("👤 Profil"): st.session_state.page = "Profil"; st.rerun()

# --- CSS FÜR BUTTONS ---
st.markdown("<style>.stButton>button { width: 100%; border-radius: 10px; }</style>", unsafe_allow_html=True)
