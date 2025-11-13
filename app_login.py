import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from streamlit_cookies_manager import EncryptedCookieManager

# =========================
# Setup
# =========================
st.set_page_config(page_title="Super Admin Panel", layout="wide")
cookies = EncryptedCookieManager(prefix="myapp", password="adminapp123")

if not cookies.ready():
    st.stop()


# =========================
# Utility Functions
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Users table now includes password
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    role TEXT)''')

    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
                    username TEXT UNIQUE,
                    password TEXT)''')
    conn.commit()
    conn.close()


def login_user(username):
    cookies['logged_in'] = 'True'
    cookies['username'] = username
    cookies.save()


def logout_user():
    cookies['logged_in'] = ''
    cookies['username'] = ''
    cookies.save()


def add_user(name, email, password, role):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
              (name, email, hashed_password, role))
    conn.commit()
    conn.close()


def view_all_users(limit, offset):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, role FROM users LIMIT ? OFFSET ?', (limit, offset))
    data = c.fetchall()
    conn.close()
    return data


def search_user_by_name_or_email(search_term):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, role FROM users WHERE name LIKE ? OR email LIKE ?',
              ('%' + search_term + '%', '%' + search_term + '%'))
    data = c.fetchall()
    conn.close()
    return data


def update_user_by_email(old_email, new_name, new_email, new_role, new_password=None):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    if new_password:
        hashed_password = hash_password(new_password)
        c.execute("UPDATE users SET name=?, email=?, role=?, password=? WHERE email=?",
                  (new_name, new_email, new_role, hashed_password, old_email))
    else:
        c.execute("UPDATE users SET name=?, email=?, role=? WHERE email=?",
                  (new_name, new_email, new_role, old_email))

    conn.commit()
    conn.close()


def delete_user_by_email(email):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE email=?', (email,))
    conn.commit()
    conn.close()


def get_user_count():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count


def create_super_admin(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM admin WHERE username = ?', (username,))
    count = c.fetchone()[0]

    if count == 0:
        hashed_password = hash_password(password)
        c.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        st.success("Admin created successfully!")

    conn.close()


def authenticate(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM admin WHERE username=? AND password=?', (username, hashed_password))
    result = c.fetchone()
    conn.close()
    return bool(result)


def get_admin():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM admin LIMIT 1')
    admin = c.fetchone()
    conn.close()
    return admin


# =========================
# Main App
# =========================
def main():
    create_tables()

    if not get_admin():
        create_super_admin('admin', 'admin')

    if cookies.get('logged_in') == 'True':
        st.title("👑 Super Admin - User Management")
    else:
        st.title("🔐 Admin Login")

    if 'page' not in st.session_state:
        st.session_state['page'] = "view_users" if cookies.get('logged_in') == 'True' else "login"

    if 'page_number' not in st.session_state:
        st.session_state['page_number'] = 1

    # ============ LOGIN ============
    if cookies.get('logged_in') != 'True' and st.session_state['page'] == "login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                login_user(username)
                st.session_state['page'] = "view_users"
                st.rerun()
            else:
                st.error("Invalid credentials")
        return

    # ============ SIDEBAR ============
    if cookies.get('logged_in') == 'True':
        with st.sidebar:
            st.header("Menu")
            if st.button("🏠 Dashboard"):
                st.session_state['page'] = "view_users"
            if st.button("➕ Add User"):
                st.session_state['page'] = "add_user"
            if st.button("🚪 Logout"):
                logout_user()
                st.session_state['page'] = "login"
                st.rerun()

    # ============ ADD USER ============
    if st.session_state['page'] == "add_user":
        st.subheader("Add New User")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Admin", "User", "Viewer"])
        if st.button("Add User", key="add_user_button"):
            if not all([name, email, password]):
                st.warning("Please fill all fields")
            else:
                try:
                    add_user(name, email, password, role)
                    st.success(f"User {name} added successfully")
                    st.session_state['page'] = "view_users"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"User with email {email} already exists.")

    # ============ VIEW USERS ============
    if st.session_state['page'] == "view_users" and cookies.get('logged_in') == 'True':
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("All Users")
        with col2:
            if st.button("Add User"):
                st.session_state['page'] = "add_user"
                st.rerun()

        search_term = st.text_input("Search", placeholder="Search by Name or Email", label_visibility="collapsed")
        per_page = 5
        user_count = get_user_count()
        max_pages = (user_count // per_page) + 1
        if st.session_state['page_number'] > max_pages:
            st.session_state['page_number'] = max_pages
        offset = (st.session_state['page_number'] - 1) * per_page

        users = search_user_by_name_or_email(search_term) if search_term else view_all_users(per_page, offset)
        if users:
            df = pd.DataFrame(users, columns=["ID", "Name", "Email", "Role"])
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 5, 2, 2, 2])
            col1.write("ID"); col2.write("Name"); col3.write("Email"); col4.write("Role"); col5.write("Edit"); col6.write("Delete")

            for index, row in df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 5, 2, 2, 2])
                col1.write(row['ID'])
                col2.write(row['Name'])
                col3.write(row['Email'])
                col4.write(row['Role'])

                if col5.button("Edit", key=f"edit_{row['Email']}"):
                    st.session_state['edit_email'] = row['Email']
                    st.session_state['page'] = "edit_user"
                    st.rerun()
                if col6.button("Delete", key=f"delete_{row['Email']}"):
                    delete_user_by_email(row['Email'])
                    st.success(f"User {row['Email']} deleted successfully")
                    st.rerun()
        else:
            st.info("No users found.")

    # ============ EDIT USER ============
    if 'edit_email' in st.session_state and st.session_state['page'] == "edit_user":
        edit_user_email = st.session_state['edit_email']
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (edit_user_email,))
        user_to_edit = c.fetchone()
        conn.close()

        if not user_to_edit:
            st.error("User not found.")
            st.session_state['page'] = 'view_users'
            st.rerun()

        st.subheader(f"Edit User: {edit_user_email}")
        new_name = st.text_input("New Name", user_to_edit[1])
        new_email = st.text_input("New Email", user_to_edit[2])
        new_role =_
