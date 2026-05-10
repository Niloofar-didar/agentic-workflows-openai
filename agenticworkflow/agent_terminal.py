import tkinter as tk
from tkinter import scrolledtext
import json
from openai.types.chat import ChatCompletionMessage
from reminderApp import (
    run_conversation,
    get_current_datetime_schema,
    process_raw_response_to_dic,
)


def start_ui(messages_history, tools_schema):
    root = tk.Tk()
    root.title("AI Agent Terminal")

    # 1. SET MINIMUM SIZE: This prevents the button from being "crushed"
    root.geometry("500x600")
    root.minsize(400, 450)

    # 2. CHAT AREA: Pack this FIRST with fill=BOTH and expand=True
    # This allows it to take all available space but yield to the bottom frame
    chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 10))
    chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    chat_area.config(state='disabled')

    # 3. BOTTOM FRAME: Pack with side=BOTTOM
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    # 4. INPUT FIELD: Using Text for multi-line
    input_field = tk.Text(bottom_frame, font=("Arial", 11), height=3, wrap=tk.WORD)
    input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    input_field.focus_set()

    def update_chat(text):
        chat_area.config(state='normal')
        chat_area.insert(tk.END, text + "\n\n")
        chat_area.config(state='disabled')
        chat_area.yview(tk.END)
        root.update()

    def handle_send(event=None):
        user_text = input_field.get("1.0", tk.END).strip()
        if not user_text:
            return "break"

        update_chat(f"User: {user_text}")
        input_field.delete("1.0", tk.END)

        messages_history.append({"role": "user", "content": user_text})

        # Agent Logic
        final_history_raw = run_conversation(messages_history, tools_schema, ui_callback=update_chat)
        final_history = process_raw_response_to_dic(final_history_raw)

        if final_history:
            last_msg = final_history[-1]
            final_answer = last_msg.get('content')
            if final_answer:
                update_chat(f"AI: {final_answer}")
            else:
                update_chat("AI: [Task Completed]")

        return "break"

    # 5. SEND BUTTON
    send_btn = tk.Button(bottom_frame, text="Send", command=handle_send, width=10, bg="#e1e1e1")
    send_btn.pack(side=tk.RIGHT)

    root.bind('<Return>', handle_send)
    root.mainloop()


if __name__ == "__main__":
    start_ui([], [get_current_datetime_schema])
