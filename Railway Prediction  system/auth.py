"""
auth.py  -  RailTrack Authentication System
Storage:  users.json  (local file, no database)
Login:    Full Name + Phone Number only
"""

import json
import datetime
from pathlib import Path
import streamlit as st

# ── Constants ──────────────────────────────────────────────────────────────────
USERS_FILE = Path("users.json")


# ── File I/O helpers ───────────────────────────────────────────────────────────

def _load_users() -> dict:
    """Load the users dictionary from disk. Returns empty dict if file missing."""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_users(users: dict) -> None:
    """Persist the users dictionary to disk."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)


# ── Core auth functions ────────────────────────────────────────────────────────

def register_user(name: str, phone: str) -> tuple[bool, str]:
    """
    Register a new user.

    Returns:
        (True, "success message")  on success
        (False, "error message")   on failure
    """
    name  = name.strip()
    phone = phone.strip().replace(" ", "").replace("-", "")

    # Validation
    if not name:
        return False, "Name cannot be empty."
    if not phone.isdigit() or len(phone) < 10:
        return False, "Phone must be at least 10 digits (numbers only)."

    users = _load_users()

    if phone in users:
        return False, "Phone already exists. Please log in instead."

    users[phone] = {
        "name":            name,
        "phone":           phone,
        "joined":          datetime.datetime.now().isoformat(),
        "journey_history": []
    }
    _save_users(users)
    return True, f"Welcome aboard, {name}! Your account has been created."


def login_user(name: str, phone: str) -> tuple[bool, str, dict | None]:
    """
    Authenticate an existing user.

    Returns:
        (True,  "success message", user_dict)   on success
        (False, "error message",   None)         on failure
    """
    name  = name.strip()
    phone = phone.strip().replace(" ", "").replace("-", "")

    if not name or not phone:
        return False, "Please enter both name and phone number.", None

    users = _load_users()

    if phone not in users:
        return False, "User not found. Please register first.", None

    if users[phone]["name"].lower() != name.lower():
        return False, "Name does not match. Please check your details.", None

    return True, f"Welcome back, {users[phone]['name']}!", users[phone]


def save_journey(phone: str, journey: dict) -> None:
    """
    Append a journey record to the user's history.

    journey dict example:
        {
            "from":          "Mumbai CST",
            "to":            "Pune Junction",
            "eta_minutes":   135,
            "distance_km":   148.2,
            "timestamp":     "2024-06-01T14:32:00"
        }
    """
    users = _load_users()
    if phone not in users:
        return
    journey.setdefault("timestamp", datetime.datetime.now().isoformat())
    users[phone]["journey_history"].append(journey)
    _save_users(users)


def logout_user() -> None:
    """Clear the session state to log the user out."""
    for key in ("authenticated", "user"):
        st.session_state.pop(key, None)


# ── CSS (matches existing RailTrack design tokens) ─────────────────────────────

AUTH_CSS = """
<style>
/* ── Auth page wrapper ───────────────────────────────────────── */
.auth-outer {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 80vh;
    padding: 3.5rem 1rem 4rem;
}
.auth-card {
    background: #ffffff;
    border: 1px solid #E7E5E4;
    border-radius: 18px;
    padding: 2.6rem 2.8rem;
    width: 100%;
    max-width: 440px;
    box-shadow: 0 4px 40px rgba(28,25,23,0.07);
    position: relative;
    overflow: hidden;
}
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #D97706, #3B5BDB);
}

/* ── Brand header ────────────────────────────────────────────── */
.auth-brand {
    text-align: center;
    margin-bottom: 1.8rem;
}
.auth-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1C1917;
    letter-spacing: -.02em;
    display: block;
}
.auth-tagline {
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: #A8A29E;
    margin-top: .3rem;
}
.auth-loco {
    font-size: 2.2rem;
    margin-bottom: .5rem;
}

/* ── Form inputs (override Streamlit defaults) ───────────────── */
.auth-card .stTextInput > div > div > input {
    background: #F7F3EE !important;
    border: 1.5px solid #E7E5E4 !important;
    border-radius: 8px !important;
    color: #1C1917 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .9rem !important;
    padding: .62rem .9rem !important;
    transition: border-color .18s !important;
}
.auth-card .stTextInput > div > div > input:focus {
    border-color: #D97706 !important;
    box-shadow: 0 0 0 3px rgba(217,119,6,.12) !important;
}
.auth-card label {
    font-size: .68rem !important;
    font-weight: 600 !important;
    letter-spacing: .09em !important;
    text-transform: uppercase !important;
    color: #78716C !important;
}

/* ── Primary button ──────────────────────────────────────────── */
.auth-card .stButton > button {
    background: #1C1917 !important;
    color: #FAFAF9 !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .88rem !important;
    font-weight: 600 !important;
    padding: .65rem 1.5rem !important;
    width: 100% !important;
    letter-spacing: .01em !important;
    transition: all .18s !important;
}
.auth-card .stButton > button:hover {
    background: #292524 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(28,25,23,.18) !important;
}

/* ── Alert banners ───────────────────────────────────────────── */
.auth-error {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 3px solid #DC2626;
    border-radius: 8px;
    padding: .75rem 1rem;
    font-size: .82rem;
    color: #991B1B;
    margin: .8rem 0;
}
.auth-success {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-left: 3px solid #059669;
    border-radius: 8px;
    padding: .75rem 1rem;
    font-size: .82rem;
    color: #065F46;
    margin: .8rem 0;
}
.auth-info {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 3px solid #D97706;
    border-radius: 8px;
    padding: .75rem 1rem;
    font-size: .82rem;
    color: #78350F;
    margin: .8rem 0;
}

/* ── Tabs ────────────────────────────────────────────────────── */
.auth-card .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #E7E5E4 !important;
    gap: 0 !important;
    margin-bottom: 1.4rem !important;
}
.auth-card .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #78716C !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .85rem !important;
    font-weight: 500 !important;
    padding: .5rem 1.3rem !important;
    margin-bottom: -2px !important;
}
.auth-card .stTabs [aria-selected="true"] {
    color: #1C1917 !important;
    border-bottom-color: #D97706 !important;
    font-weight: 700 !important;
}

/* ── Divider / helper text ───────────────────────────────────── */
.auth-hint {
    font-size: .75rem;
    color: #A8A29E;
    text-align: center;
    margin-top: .9rem;
}
.auth-divider {
    border: none;
    border-top: 1px solid #E7E5E4;
    margin: 1.3rem 0;
}

/* ── Top-bar logout pill ─────────────────────────────────────── */
.logout-row {
    display: flex;
    align-items: center;
    gap: .6rem;
}
.user-pill {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: rgba(217,119,6,.1);
    border: 1px solid rgba(217,119,6,.28);
    border-radius: 100px;
    padding: .28rem .85rem;
    font-size: .72rem;
    font-weight: 600;
    color: #D97706;
    letter-spacing: .05em;
}
</style>
"""


# ── Streamlit UI ───────────────────────────────────────────────────────────────

def show_auth_page() -> None:
    """
    Render the full-page login / register UI.
    Sets st.session_state['authenticated'] = True and
         st.session_state['user']          = <user dict>
    on successful login or registration.
    """
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Centre the card using Streamlit columns
    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        st.markdown("""
        <div class="auth-card">
            <div class="auth-brand">
                <span class="auth-loco">🚂</span>
                <span class="auth-logo">RailTrack</span>
                <span class="auth-tagline">ETA Prediction System</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # We render the tabs *inside* the column (not inside the raw HTML div)
        # so Streamlit widgets work correctly.
        tab_login, tab_register = st.tabs(["  Login", " Register"])

        # ── Login tab ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown(
                '<p style="font-size:.82rem;color:#78716C;margin-bottom:1rem;">'
                'Enter your registered name and phone to continue.</p>',
                unsafe_allow_html=True
            )
            login_name  = st.text_input("Full Name",     key="li_name")
            login_phone = st.text_input("Phone Number",  key="li_phone",
                                        help="10-digit mobile number, no spaces or dashes")

            if st.button("Login →", key="btn_login"):
                ok, msg, user = login_user(login_name, login_phone)
                if ok:
                    st.session_state["authenticated"] = True
                    st.session_state["user"]           = user
                    st.markdown(f'<div class="auth-success">✓ {msg}</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f'<div class="auth-error">✗ {msg}</div>', unsafe_allow_html=True)

            st.markdown('<p class="auth-hint">Don\'t have an account? Switch to the Register tab.</p>',
                        unsafe_allow_html=True)

        # ── Register tab ───────────────────────────────────────────────────────
        with tab_register:
            st.markdown(
                '<p style="font-size:.82rem;color:#78716C;margin-bottom:1rem;">'
                'Create a free account — no password needed.</p>',
                unsafe_allow_html=True
            )
            reg_name  = st.text_input("Full Name",    key="rg_name",  placeholder="e.g. Arjun Mehta")
            reg_phone = st.text_input("Phone Number", key="rg_phone", placeholder="e.g. 9123456789",
                                      help="Must be at least 10 digits")

            st.markdown(
                '<div class="auth-info" style="margin-bottom:.8rem;">'
                ' Your phone number is your unique ID — remember it for future logins.</div>',
                unsafe_allow_html=True
            )

            if st.button("Create Account →", key="btn_register"):
                ok, msg = register_user(reg_name, reg_phone)
                if ok:
                    # Auto-login after registration
                    _, _, user = login_user(reg_name, reg_phone)
                    st.session_state["authenticated"] = True
                    st.session_state["user"]           = user
                    st.markdown(f'<div class="auth-success">✓ {msg}</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f'<div class="auth-error">✗ {msg}</div>', unsafe_allow_html=True)

            st.markdown('<p class="auth-hint">Already registered? Switch to the Login tab.</p>',
                        unsafe_allow_html=True)


def show_user_pill() -> None:
    """
    Render a compact user pill + logout button suitable for the top-bar.
    Call this inside the same st.columns / HTML context as the top-bar.
    """
    user = st.session_state.get("user", {})
    name = user.get("name", "User")
    initial = name[0].upper()

    col_pill, col_btn = st.columns([3, 1])
    with col_pill:
        st.markdown(
            f'<span class="user-pill">👤 {initial} &nbsp;{name}</span>',
            unsafe_allow_html=True
        )
    with col_btn:
        if st.button("Logout", key="btn_logout"):
            logout_user()
            st.rerun()


def require_auth() -> bool:
    """
    Gate function. Call at the top of app.py.
    Returns True if the user is authenticated; shows login page and returns
    False otherwise.

    Usage in app.py:
        from auth import require_auth
        if not require_auth():
            st.stop()
    """
    if st.session_state.get("authenticated"):
        return True
    show_auth_page()
    return False