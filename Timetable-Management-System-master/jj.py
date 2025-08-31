import tkinter as tk
from tkinter import messagebox
import oracledb
import os
import admin_screen
import timetable_fac
import timetable_stud

# ---------------- DB CONNECTION ----------------
try:
    connection = oracledb.connect(
        user="system",
        password="student",
        dsn="localhost:1521/xe"  # Thin mode not supported for old DB, use thick mode
    )
except oracledb.Error as e:
    messagebox.showerror("Database Error", f"Cannot connect to database:\n{e}")
    exit()

# ---------------- LOGIN WINDOW ----------------
m = tk.Tk()
m.geometry("400x300")
m.title("Login")

tk.Label(m, text="Select User Type", font=("Consolas", 12, "bold")).pack(pady=10)
user_var = tk.StringVar(value="Admin")
tk.OptionMenu(m, user_var, "Admin", "Faculty", "Student").pack(pady=5)

tk.Label(m, text="User ID", font=("Consolas", 11)).pack(pady=5)
id_entry = tk.Entry(m, font=("Consolas", 11))
id_entry.pack()

tk.Label(m, text="Password", font=("Consolas", 11)).pack(pady=5)
passw_entry = tk.Entry(m, show="*", font=("Consolas", 11))
passw_entry.pack()

# ---------------- LOGIN FUNCTION ----------------
def login():
    user = user_var.get()
    uid = id_entry.get().strip()
    pwd = passw_entry.get().strip()

    if not uid or not pwd:
        messagebox.showwarning("Input Error", "Please enter both ID and Password")
        return

    if user == "Admin":
        if uid == "admin" and pwd == "admin":
            m.withdraw()
            os.system("python admin.py")
        else:
            messagebox.showerror("Login Failed", "Invalid Admin credentials")

    elif user == "Faculty":
        cursor = connection.cursor()
        cursor.execute(
            "SELECT PASSW, INI, NAME, EMAIL FROM FACULTY WHERE FID = :fid",
            {"fid": uid}
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            messagebox.showwarning("Login Failed", "No such faculty found")
        elif pwd != row[0]:
            messagebox.showerror("Login Failed", "Incorrect Password")
        else:
            nw = tk.Toplevel(m)
            nw.title("Faculty Panel")
            tk.Label(
                nw,
                text=f"{row[2]} ({row[1]})\tEmail: {row[3]}",
                font=("Consolas", 12, "italic")
            ).pack(pady=10)
            timetable_fac.fac_tt_frame(nw, row[1])

    elif user == "Student":
        cursor = connection.cursor()
        cursor.execute(
            "SELECT PASSW, RNO, NAME, EMAIL FROM STUDENT WHERE SID = :sid",
            {"sid": uid}
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            messagebox.showwarning("Login Failed", "No such student found")
        elif pwd != row[0]:
            messagebox.showerror("Login Failed", "Incorrect Password")
        else:
            nw = tk.Toplevel(m)
            nw.title("Student Panel")
            tk.Label(
                nw,
                text=f"{row[2]} (Roll No: {row[1]})\tEmail: {row[3]}",
                font=("Consolas", 12, "italic")
            ).pack(pady=10)
            timetable_stud.stud_tt_frame(nw, row[1])

# ---------------- BUTTONS ----------------
tk.Button(m, text="Login", font=("Consolas", 11), command=login).pack(pady=15)
tk.Button(m, text="Quit", font=("Consolas", 11), command=m.destroy).pack()

m.mainloop()

