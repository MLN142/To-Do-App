import streamlit as st
from supabase import create_client,Client
from dotenv import load_dotenv
import os

load_dotenv()

url=os.getenv("SUPABASE_URL")
key=os.getenv("SUPABASE_KEY")

supabase: Client=create_client(url,key)

def get_todos():
  response=supabase.table("todos").select("*").execute()
  return response.data

def add_todos(task):
  supabase.table("todos").insert({'task':task}).execute()

def remove_task(task):
  return None

st.title("TO-DO APP")

task=st.text_input("Enter the task to be addded")

cols=st.columns(2)
tb=st.button("Add Task")
if tb:
  if task:
    add_todos(task)
    st.success("Successfully added task!")
  else:
    st.error("Please enter a task!")


st.write("### To-Do List:")
todos=get_todos()
if todos:
  for todo in todos:
    st.write(f"{todo["task"]}")
else:
  st.write("No task available!")
