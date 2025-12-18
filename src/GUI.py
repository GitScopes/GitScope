import customtkinter as ctk
from search_github import search_repos  # Import your function

app = ctk.CTk()
app.title("GitScope")
app.geometry("600x500")

# Title
title = ctk.CTkLabel(app, text="GitScope", font=("Arial", 28, "bold"))
title.pack(pady=30)

# Search box
search_entry = ctk.CTkEntry(app, width=400, placeholder_text="Search repositories...")
search_entry.pack(pady=10)


# Search button
def search_clicked():
    query = search_entry.get()
    repos = search_repos(query)  # Uses defaults: stars, desc, 10

    # Clear old results
    for widget in results_frame.winfo_children():
        widget.destroy()

    # Show new results
    for repo in repos:
        result_btn = ctk.CTkButton(
            results_frame, text=f"{repo['full_name']} ⭐ {repo['stars']}", anchor="w"
        )
        result_btn.pack(pady=5, fill="x")


search_button = ctk.CTkButton(app, text="Search", command=search_clicked)
search_button.pack(pady=10)

# Results area
results_frame = ctk.CTkScrollableFrame(app, width=500, height=300)
results_frame.pack(pady=20)

app.mainloop()
