import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import requests
import os

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Multilingual Chatbot")

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', height=20)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User input
        self.user_input = tk.Text(master, height=2)
        self.user_input.pack(padx=10, pady=10, fill=tk.X)

        # Language selection
        self.language_var = tk.StringVar(value="French")
        language_label = tk.Label(master, text="Select Language:")
        language_label.pack(pady=5)
        language_menu = tk.OptionMenu(master, self.language_var, "French", "Spanish", "German", "Italian")
        language_menu.pack(pady=5)

        # API Key Input
        self.api_key = self.load_api_key()

        # Frame for buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=5)  # Pack the frame with some vertical space

        # Send button
        self.send_button = tk.Button(self.button_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)  # Pack button to the left with padding

        # Save chat button
        self.save_button = tk.Button(self.button_frame, text="Save Chat", command=self.save_chat)
        self.save_button.pack(side=tk.LEFT, padx=5)  # Pack button to the left with padding

        # Clear chat button
        self.clear_button = tk.Button(self.button_frame, text="Clear Chat", command=self.clear_chat)
        self.clear_button.pack(side=tk.LEFT, padx=5)  # Pack button to the left with padding

        # Retrieve last chats button
        self.retrieve_button = tk.Button(self.button_frame, text="Retrieve Last Chats", command=self.retrieve_last_chats)
        self.retrieve_button.pack(side=tk.LEFT, padx=5)  # Pack button to the left with padding

        # Load previous chat history
        self.load_chat_history()

    def load_api_key(self):
        # Load API key from environment variable or ask user
        api_key = os.getenv("NEUROCHAIN_API_KEY")  # Consider setting this environment variable
        if not api_key:
            api_key = simpledialog.askstring("API Key", "Enter your API Key:")
        return api_key

    def send_message(self):
        user_text = self.user_input.get("1.0", tk.END).strip()
        if user_text:
            self.update_chat(f"You: {user_text}")
            self.show_loading()  # Show loading while fetching response
            translation = self.get_translation(user_text)
            self.update_chat(f"Bot: {translation}")
            self.user_input.delete("1.0", tk.END)

    def update_chat(self, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)  # Scroll to the bottom

    def show_loading(self):
        self.update_chat("Bot is typing...")

    def get_translation(self, text):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "Mistral-7B-Instruct-v0.2-GPTQ",
            "prompt": f"Translate the following text to {self.language_var.get()}: {text}",
            "max_tokens": 1024,
            "temperature": 0.6,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 1.1
        }
        try:
            response = requests.post("https://ncmb.neurochain.io/tasks/message", headers=headers, json=data)
            response.raise_for_status()  # Raises an error for bad responses
            return response.json().get('result', 'Translation not found.')
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                error_detail = response.json().get('msg', 'Bad request')
                messagebox.showerror("Error", f"400 Bad Request: {error_detail}")
            else:
                messagebox.showerror("Error", f"HTTP error occurred: {http_err}")
            return "Error"
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return "Error"

    def save_chat(self):
        chat_history = self.chat_area.get("1.0", tk.END).strip()
        if chat_history:
            try:
                with open("chat_history.txt", "w") as file:
                    file.write(chat_history)
                messagebox.showinfo("Success", "Chat history saved to chat_history.txt")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chat: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No chat history to save.")

    def clear_chat(self):
        # Clear the chat area
        self.chat_area.configure(state='normal')
        self.chat_area.delete("1.0", tk.END)  # Clear the chat history in the UI
        self.chat_area.configure(state='disabled')

    def retrieve_last_chats(self):
        # Retrieve the last few lines of chat history from the file
        try:
            if os.path.exists("chat_history.txt"):
                with open("chat_history.txt", "r") as file:
                    lines = file.readlines()
                    last_lines = lines[-5:]  # Get the last 5 lines
                    self.chat_area.configure(state='normal')
                    self.chat_area.insert(tk.END, "Last Chats:\n" + ''.join(last_lines))
                    self.chat_area.configure(state='disabled')
            else:
                messagebox.showwarning("Warning", "No chat history file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve chat history: {str(e)}")

    def load_chat_history(self):
        try:
            if os.path.exists("chat_history.txt"):
                with open("chat_history.txt", "r") as file:
                    chat_history = file.read()
                    self.chat_area.configure(state='normal')
                    self.chat_area.insert(tk.END, chat_history)
                    self.chat_area.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chat history: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
