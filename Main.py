import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  



def get_client() -> Client:
    if "supabase" not in st.session_state:
        st.session_state["supabase"] = create_client(SUPABASE_URL, SUPABASE_KEY)
    return st.session_state["supabase"]



def sign_up(email, password):
    try:
        return get_client().auth.sign_up({"email": email, "password": password})
    except Exception as e:
        st.error(f"Registration failed: {e}")


def sign_in(email, password):
    try:
        return get_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        st.error(f"Login failed: {e}")


def sign_out():
    try:
        get_client().auth.sign_out()
    except Exception as e:
        st.error(f"Logout failed: {e}")
    # drop the whole per-user client so nothing lingers
    st.session_state.pop("supabase", None)
    st.session_state["user"] = None
    st.session_state["current_page"] = "log_in"
    st.rerun()


def make_current_page(name):
    st.session_state["current_page"] = name



def get_todos():
    user = st.session_state["user"]
    res = (
        get_client()
        .table("todos")
        .select("*")
        .eq("user_id", user.id)
        .order("id")
        .execute()
    )
    return res.data


def add_todo(task):
    user = st.session_state["user"]
    get_client().table("todos").insert({"task": task, "user_id": user.id}).execute()


def remove_todo(todo_id):
    user = st.session_state["user"]
    (
        get_client()
        .table("todos")
        .delete()
        .eq("id", todo_id)
        .eq("user_id", user.id)
        .execute()
    )


def handle_add_task():
    task = st.session_state.get("task_input", "").strip()
    if task:
        try:
            add_todo(task)
            st.session_state["task_input"] = ""  # clear the box
            st.session_state["flash"] = ("success", "Successfully added task!")
        except Exception as e:
            st.session_state["flash"] = ("error", f"Could not add task: {e}")
    else:
        st.session_state["flash"] = ("error", "Please enter a task!")


# ---------------------------------------------------------------

def main_page():
    user = st.session_state["user"]

    top = st.columns([8, 2])
    top[0].title("TO-DO APP")
    if top[1].button("Sign out"):
        sign_out()
    st.caption(f"Logged in as {user.email}")

    st.text_input(
        "Enter the task to be added", placeholder="Type here", key="task_input"
    )
    st.button("Add Task", on_click=handle_add_task)

    flash = st.session_state.pop("flash", None)
    if flash:
        (st.success if flash[0] == "success" else st.error)(flash[1])

    st.write("### To-Do List:")
    try:
        todos = get_todos()
    except Exception as e:
        st.error(f"Could not load tasks: {e}")
        todos = []

    if todos:
        for todo in todos:
            col1, col2 = st.columns([8, 2])
            col1.write(todo["task"])
            col2.button(
                "Remove Task",
                key=f"del_{todo['id']}",
                on_click=remove_todo,
                args=(todo["id"],),
            )
    else:
        st.write("No task available!")


def sign_up_page():
    st.title("Sign-Up")
    email = st.text_input("Email", key="sign_up_email")
    password = st.text_input("Password", type="password", key="sign_up_password")
    cols = st.columns([7, 1])
    with cols[0]:
        sign_up_button = st.button("Sign-Up", key="sign_up_button")
    with cols[1]:
        st.button("Return", on_click=make_current_page, args=("log_in",))

    if sign_up_button:
        if not (email and password):
            st.error("Please enter email and password")
        else:
            result = sign_up(email, password)
            if result:
                st.success("Successfully signed up. Please confirm your email.")


def log_in_page():
    st.title("To-Do App Authentication")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    cols = st.columns([7, 1])
    with cols[0]:
        login_button = st.button("Login")
    with cols[1]:
        st.button("Sign-Up", on_click=make_current_page, args=("sign_up",))

    if login_button:
        if not (email and password):
            st.error("Please enter email and password")
        else:
            with st.spinner("Logging in"):
                result = sign_in(email, password)
            if result and result.user:
                st.session_state["user"] = result.user
                st.rerun()


# ---------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["current_page"] = "log_in"

if st.session_state["user"]:
    main_page()
elif st.session_state["current_page"] == "sign_up":
    sign_up_page()
else:
    log_in_page()