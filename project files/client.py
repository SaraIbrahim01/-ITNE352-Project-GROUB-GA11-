# News Service Client - GUI Version (Tkinter)


import socket
import threading
import tkinter as tk
from tkinter import scrolledtext , messagebox


# Server settings (change HOST if the server is on another machine)

SERVER_HOST = "127.0.0.1"      # Server settings-> (change HOST if the server is on another machine)
SERVER_PORT = 5000             #  Must match your server port 

class NewsClientGUI:
    def __init__(self, root: tk.Tk):       # Initialize the GUI window and build the login screen.
      self.root = root
      self.root.title("News Client - GUI Version") 

      self.sock: socket.socket | None = None       # TCP socket connection
      self.username: str =""                        # User's chosen name

      self.build_login_screen()                   # Create the login page first

 # When the window closes, run cleanup
      self.root.protocol("WM_DELETE_WINDOW", self.on_close)

# Utility: Remove all widgets from the window
    def clear_window(self):
       for widget in self.root.winfo_children():
          widget.destroy()

 # Login screen (username + connect button)
    def build_login_screen(self):
       self.clear_window()

       tk.Label(
          self.root, text="Enter your username:", font=("Arial", 14)
       ).pack(pady=10)

 # Text field for username 
       self.username_entry = tk.Entry(self.root, font=("Arial", 14))  
       self.username_entry.pack(pady=5) 

 # Button to connect to the server
       tk.Button(
         self.root,
         text="Connect",
         font=("Arial", 14),
         command= self.connect_to_server
    ).pack(pady=10)

 # Connect to server and send username
    def connect_to_server(self):
       username= self.username_entry.get().strip()
       if not username:
          messagebox.showerror("Error", "Please enter a username ")
          return
       self.username= username

       try:
       
           self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           self.sock.connect((SERVER_HOST, SERVER_PORT))
       except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.sock=None
            return
    
       try:
       
           self.sock.sendall((self.username + "\n").encode("utf-8"))
       except Exception as e:
            messagebox.showerror("Send Error", str(e))
            self.sock.close()
            self.sock = None
            return
    
       self.build_chat_screen()


       recv_thread =threading.Thread(target=self.receive_loop, daemon=True)
       recv_thread.start()

 # Main GUI for interacting with server
    
    def build_chat_screen(self): 
       self.clear_window()

       tk.Label(
          self.root,
          text=f"Connected as:{self.username}",
          font=("Arial",12,"bold")
       ).pack(pady=5)

 # Scrollable text area to display server messages
       self.text_area = scrolledtext.ScrolledText(
         self.root,
         width=80,
         height=25,
         font=("Consolas",11)
    )
       self.text_area.pack(padx=10, pady=5)
       self.text_area.config(state=tk.DISABLED)

       bottom_frame = tk.Frame(self.root)
       bottom_frame.pack(pady=5)

       self.input_entry = tk.Entry(bottom_frame, font=("Arial", 12), width=40)
       self.input_entry.pack(side=tk.LEFT, padx=5)

       tk.Button(
          bottom_frame,
          text="Send",
          font=("Arial", 12),
          command=self.send_input
      ).pack(side=tk.LEFT, padx=5) 

       tk.Button(
          bottom_frame,
          text="Quit",
          font=("Arial", 12 ),
          command=self.quit_client
      ).pack(side=tk.LEFT, padx=5)

       self.root.bind("<Return>", lambda event: self.send_input())

# Add text messages from server into the GUI text area
    def append_text(self, text: str):
       self.text_area.config(state=tk.NORMAL)
       self.text_area.insert(tk.END, text)
       self.text_area.see(tk.END)
       self.text_area.config(state=tk.DISABLED)

# Receiving loop (runs in a background thread)
    def receive_loop(self):
        if not self.sock:
          return
         
        try:
          while True:
            data= self.sock.recv(4096)
            if not data:
              self.append_text("\n[Disconnected from server]\n")
              break
            self.append_text(data.decode("utf-8"))

        except:
           self.append_text("\n[Connection error]\n")

 # Send user input to the server
    def send_input(self):
       if not self.sock:
          messagebox.showerror("Error", "Not connected to server ")
          return
       
       user_input= self.input_entry.get().strip()
       if not user_input:
          return
       try:
          self.sock.sendall((user_input+ "\n").encode("utf-8"))
    
       except:
          self.append_text("\n[Failed to send message]\n")
          return
       
       self.input_entry.delete(0, tk.END)
      
 # Graceful exit from the application
    def quit_client(self):
       try:
          if self.sock:
             self.sock.sendall(b"4\n")
       except:
          pass
       self.root.destroy()

# Cleanup on window close
    def on_close(self):
       if self.sock:
          try:
             self.sock.close()
          except:
             pass
          self.root.destroy()

# Program entry point
root= tk.Tk()
app= NewsClientGUI(root)
root.mainloop()

   




       
       
       
  


       




    



     
       



