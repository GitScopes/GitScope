import customtkinter as ctk
from search_github import search_repos  # Import your function

app = ctk.CTk()
app.title("GitScope")
app.geometry("600x500")

search_frame = ctk.CTkFrame(app)

# Title
title = ctk.CTkLabel(search_frame, text="GitScope", font=("Arial", 28, "bold"))
title.pack(pady=30)

# Search box
search_entry = ctk.CTkEntry(
    search_frame, width=400, placeholder_text="Search repositories..."
)
search_entry.pack(pady=10)


def show_details(repo):
    search_frame.pack_forget()
    details_frame.pack(fill="both", expand=True)
    repo_name_label.configure(text=repo["full_name"])


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
            results_frame,
            text=f"{repo['full_name']} ⭐ {repo['stars']}",
            anchor="w",
            command=lambda r=repo: show_details(r),
        )
        result_btn.pack(pady=5, fill="x")


search_button = ctk.CTkButton(search_frame, text="Search", command=search_clicked)
search_button.pack(pady=10)

# Results area
results_frame = ctk.CTkScrollableFrame(search_frame, width=500, height=300)
results_frame.pack(pady=20)

# ---details_frame---

details_frame = ctk.CTkFrame(app)

repo_name_label = ctk.CTkLabel(details_frame, text="", font=("Arial", 24))
repo_name_label.pack(pady=50)

back_button = ctk.CTkButton(
    details_frame,
    text="Back",
    command=lambda: [
        details_frame.pack_forget(),
        search_frame.pack(fill="both", expand=True),
    ],
)
back_button.pack()
search_frame.pack(fill="both", expand=True)
app.mainloop()
