import socket
from customtkinter import *
from PIL import Image
import webbrowser
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 5678))

def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

# pagina cu cautari de filme la care sa se poata reveni
# e un frame care va fi adaugat la fereastra principala
def primary_page(window):

    def send_to_server():
        search_movie = widget4.get()
        s.sendall(search_movie.encode("utf-8"))

        secondary_page(window)

    primary_frame = CTkFrame(window, width=850, height=570)
    primary_frame.grid_propagate(False)
    primary_frame.grid(row=0, column=0)

    my_img = CTkImage(dark_image = Image.open("bgimg22.jpeg"), size = (520, 550))
    lab = CTkLabel(primary_frame, text='', image = my_img)
    lab.grid(row=0, column=0)

    frame = CTkFrame(primary_frame, width=330, height=550, fg_color="#353540")
    frame.grid_propagate(False)
    frame.grid(row=0, column=1)

    widget1 = CTkLabel(master=frame, text="Magic Movies", text_color="#d1d2d2", justify="center", font=("Arial Bold", 24))
    widget2 = CTkLabel(master=frame, text="Search for a movie rating", text_color="#d1d2d2", justify="center", font=("Arial Italic", 12))

    widget3 = CTkLabel(master=frame, text="Search by movie title or by actors:", text_color="#d1d2d2", justify="center", font=("Arial", 14), compound="left")
    widget4 = CTkEntry(master=frame, placeholder_text="search...", width=280, fg_color="#EEEEEE", border_color="#152f54", border_width=1, text_color="#000000")

    widget5 = CTkButton(master=frame, text="Search a movie", command=send_to_server, fg_color="#3a98ca", hover_color="#dc6d12", font=("Arial", 12), text_color="white", width=225)

    widget1.grid(row=0, column=0, pady=(100, 5), padx=(25, 0))
    widget2.grid(row=1, column=0, pady=(0, 5), padx=(25, 0))
    widget3.grid(row=2, column=0, pady=(38, 0), padx=(25, 0))
    widget4.grid(row=3, column=0, pady=(0, 5), padx=(25, 0))
    widget5.grid(row=4, column=0, pady=(25, 0), padx=(25, 0))

def secondary_page(window):
    full_message = ""

    start_time = time.time()
    while True:     
        msg = s.recv(2048)
        if not msg:
            break

        decoded_msg = msg.decode("utf-8")
        full_message += decoded_msg

        if "The end of the results" in decoded_msg:
            break
    
    #print(full_message)

    clear_window(window)

    secondary_frame = CTkScrollableFrame(window, width=810, height=520)
    secondary_frame.grid(row=0, column=0, padx = (10, 10), pady = (10, 10))

    my_img = CTkImage(dark_image = Image.open("cinema.jpg"), size = (550, 180))
    lab = CTkLabel(secondary_frame, text='', image = my_img)
    lab.grid(row=0, column=0)

    i_row = 1
    parts = full_message.split('(section)')
    for part in parts:
        if "Rating" in part:
            widget = CTkLabel(secondary_frame, text=part, text_color="#d1d2d2", justify="left", font=("Arial Bold", 18))
            widget.grid(row=i_row, column=0, sticky='w')
            i_row += 1
            count = 1
        
        if "Rotten Tomatoes rating" in part:
            print(part)
            widget = CTkLabel(secondary_frame, text=part, text_color="#d1d2d2", justify="left", font=("Arial Bold", 18))
            widget.grid(row=i_row, column=0, sticky='w')
            i_row += 1
        
        if "https://www.youtube.com/watch?" in part:
            widget = CTkLabel(secondary_frame, text=f"Trailer {count}", text_color = '#80ccff',
                       cursor = 'hand2', font=('Arial', 20, 'underline'))
            widget.grid(row=i_row, column=0, sticky='w')
            widget.bind('<Button-1>', lambda event, link=part: webbrowser.open_new(link))
            count += 1
            i_row += 1
        
        if "https://www.youtube.com/results?" in part:
            #print(part)
            widget = CTkLabel(secondary_frame, text="TRAILERS", text_color = '#80ccff',
                       cursor = 'hand2', font=('Arial', 20, 'underline'))
            widget.grid(row=i_row, column=0, sticky='w')
            widget.bind('<Button-1>', lambda event, link=part: webbrowser.open_new(link))
            i_row += 1

        if "Users reviews" in part:
            widget = CTkLabel(secondary_frame, text=part, text_color="#d1d2d2", justify="left", font=("Arial Bold", 18))
            widget.grid(row=i_row, column=0, sticky='w')
            i_row += 1
        
        if "The end of the results" in part:
            #print(part)
            widget = CTkLabel(secondary_frame, text=part, text_color="#d1d2d2", justify="left", font=("Arial Bold", 18))
            widget.grid(row=i_row, column=0, sticky='w')
            i_row += 1

    widget3 = CTkButton(secondary_frame, text="Back to searching", command=lambda:primary_page(window), fg_color="#3a98ca", hover_color="#dc6d12", font=("Arial", 12), text_color="white", width=225)
    widget3.grid(row=i_row, column=0, pady=(25, 0))

    end_time = time.time()
    duration = end_time - start_time
    print(duration)


# singura fereastra a aplicatiei (voi comuta intre frame-uri)
def main_window():
    app = CTk()
    app.geometry("850x550")
    app.title("Movies")
    app.resizable(0,0)
    set_appearance_mode("dark")
    primary_page(app)
    app.mainloop()

main_window()




