from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pygame import mixer
import time
from models.song import Song
from models.playlist import Playlist, PlaylistItem
from handlers.database import DatabaseHandler
import sqlalchemy
from sqlalchemy.exc import IntegrityError

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

# Store Current Playlist Name
global selected_playlist

# Store Current Song Location
global song_location

# Store Song Length In Milliseconds
global song_length

# Store Song Length In 00:00 Format
global converted_song_length


# ----------------------------------------------------------------------------------------------------------------------
# Menu Commands
def choose_playlist():
    def exit_new_window():
        # Playlist Name
        global selected_playlist
        selected_playlist = playlist_select.get(ACTIVE)

        # Close New Window
        new_window.destroy()

        stop()
        playlist_box.delete(0, END)

        # Get Songs From Playlist
        songs = get_songs()

        # Display Playlist Name
        playlist_name.config(text=selected_playlist)

        for song in songs:
            # Add Each Song In playlist_box
            playlist_box.insert(END, song)

    session = DatabaseHandler.session

    # Create New Window
    new_window = Tk()
    new_window.geometry('180x185')
    new_window.title('')
    new_window.iconbitmap('images/icon.ico')

    # Display All Playlists
    playlist_select = Listbox(new_window, selectbackground='#6666ff', activestyle='none')
    playlist_select.pack(side=TOP, fill=X)

    # Get All Playlists From Database
    db_playlist = session.query(Playlist).all()
    for playlist in db_playlist:
        # Add Playlist Name For Displaying
        playlist_select.insert(END, playlist.playlist_name)

    # Button To Select The Playlist
    btn = Button(new_window, text='Done', borderwidth=0, command=exit_new_window, bg='grey', fg='white')
    btn.pack(side=BOTTOM, fill=X)

    # Display New Window
    new_window.mainloop()


def create_playlist():
    def exit_new_window():
        # Get Input String
        name = textbox.get()

        # Close New Window
        new_window.destroy()

        session = DatabaseHandler.session
        playlist = Playlist()

        # Add String To Database
        playlist.playlist_name = name
        session.add(playlist)

        # Check For Duplicate Playlist
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            messagebox.showerror('Error', 'Duplicate Playlist')

    # Initialize New Window
    new_window = Tk()
    new_window.title('')
    new_window.iconbitmap('images/icon.ico')

    # Create Frame
    frame = Frame(new_window)
    frame.pack()

    # Create Textbox For Typing Playlist Name
    textbox = ttk.Entry(frame, width=30)
    textbox.grid(row=0, column=0)

    # Create Button To Submit Playlist Name
    btn = Button(frame, text='Done', borderwidth=0, command=exit_new_window, bg='grey', fg='white')
    btn.grid(row=0, column=1)

    # Display New Window
    new_window.mainloop()


def delete_playlist():
    def exit_new_window():
        # Playlist Name
        playlist_to_delete = playlist_select.get(ACTIVE)

        # Close New Window
        new_window.destroy()

        # If Current Playlist Is Deleted Stop Song And Reinitialize playlist_box
        if playlist_to_delete == selected_playlist:
            stop()
            playlist_box.delete(0, END)
            playlist_name.config(text='')

        # Remove Items From Playlist
        session.query(PlaylistItem).filter(PlaylistItem.playlist_id == Playlist.id,
                                           Playlist.playlist_name == playlist_to_delete).delete(
                                            synchronize_session=False)

        # Delete Playlist
        session.query(Playlist).filter(Playlist.playlist_name == playlist_to_delete).delete(synchronize_session=False)

        # Save Changes To Database
        session.commit()

    session = DatabaseHandler.session

    # Create New Window
    new_window = Tk()
    new_window.geometry('180x185')
    new_window.title('')
    new_window.iconbitmap('images/icon.ico')

    # Display All Playlists
    playlist_select = Listbox(new_window, selectbackground='#6666ff', activestyle='none')
    playlist_select.pack(side=TOP, fill=X)

    # Get All Playlists From Database
    db_playlist = session.query(Playlist).all()
    for playlist in db_playlist:
        # Add Playlist Name For Displaying
        playlist_select.insert(END, playlist.playlist_name)

    # Button To Select The Playlist
    btn = Button(new_window, text='Delete', borderwidth=0, command=exit_new_window, bg='grey', fg='white')
    btn.pack(side=BOTTOM, fill=X)

    # Display New Window
    new_window.mainloop()

    stop()


def browse_files():
    # Search For File/Files In Computer And Return It
    filename = filedialog.askopenfilenames()
    return filename


def add_song():
    # Search For Files In PC
    songs = browse_files()

    session = DatabaseHandler.session

    # Get Each Song From songs List
    for song in songs:
        # Save Song Location
        song_to_add = Song()
        song_to_add.location = song

        # Remove Song Location And Extension
        song = song.replace('E:/GitLab/python_project/audio/', '')
        song = song.replace('.mp3', '')

        # Save Song Title
        song_to_add.title = song

        # Check If Song Exists In Database
        exists = session.query(Song.title).filter_by(title=song_to_add.title).scalar() is not None

        # If Song Not In Database, Then Add It
        if exists is False:
            # Add Song To Database
            session.add(song_to_add)

        # Create Connexion Between 'Song' And 'Playlists' Tabels
        item_to_add = PlaylistItem()
        item_to_add.song_id = session.query(Song.id).filter_by(title=song_to_add.title)
        item_to_add.playlist_id = session.query(Playlist.id).filter_by(playlist_name=selected_playlist)

        # Check If Song In Playlist
        exists = session.query(PlaylistItem).filter(
            PlaylistItem.song_id == item_to_add.song_id,
            PlaylistItem.playlist_id == item_to_add.playlist_id).scalar() is not None

        # If Song Not In Playlist, Then Add It
        if exists is False:
            # Add Song To Playlist
            session.add(item_to_add)

    # Save Changes To Database
    session.commit()

    # Get Songs From Playlist
    songs = get_songs()

    # Clear playlist_box
    playlist_box.delete(0, END)

    for song in songs:
        # Add Each Song In playlist_box
        playlist_box.insert(END, song)


def remove_song():
    session = DatabaseHandler.session

    # Get Selected Song
    song_to_delete = playlist_box.get(ACTIVE)[0]

    # Get Item To Delete
    item_to_delete = session.query(PlaylistItem.id).filter(PlaylistItem.song_id == Song.id,
                                                           Song.title == song_to_delete,
                                                           PlaylistItem.playlist_id == Playlist.id,
                                                           Playlist.playlist_name == selected_playlist)

    # Delete Selected Song From Playlist
    session.query(PlaylistItem).filter_by(id=item_to_delete).delete(synchronize_session=False)
    session.commit()

    # Get Songs From Playlist
    songs = get_songs()

    # Clear playlist_box
    playlist_box.delete(0, END)

    for song in songs:
        # Add Each Song In playlist_box
        playlist_box.insert(END, song)

    stop()


def get_songs():
    session = DatabaseHandler.session

    # Get Songs From Playlist
    songs = session.query(Song.title).filter(PlaylistItem.song_id == Song.id,
                                             PlaylistItem.playlist_id == Playlist.id,
                                             Playlist.playlist_name == selected_playlist)

    return songs


# ----------------------------------------------------------------------------------------------------------------------
# Control Buttons Commands
def play():
    session = DatabaseHandler.session

    # If Playlist Is Not Empty, Run
    # Otherwise Ignore Error
    try:
        # Get Selected Song Name
        song = playlist_box.get(ACTIVE)[0]

        # Get Selected Song Location
        global song_location
        song_location = session.query(Song.location).filter_by(title=song).first()[0]

        # Load And Play Selected Song
        mixer.music.load(song_location)
        mixer.music.play()

        # Change Play Button Image To Pause Image
        play_btn.configure(image=pause_btn_img, command=pause)

        # Get Song Length
        global song_length
        song_length = mixer.Sound(song_location).get_length()

        # Convert Song Length And Store It
        global converted_song_length
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

        song_time_status()
    except IndexError:
        pass


def pause():
    # If 'Play Button Image' Is 'Play Image' (Song Has Been Paused), Change It Back To 'Pause Image' And Resume Song
    if play_btn.cget('image') == str(play_btn_img):
        mixer.music.unpause()
        play_btn.configure(image=pause_btn_img)
    # If 'Play Button Image' Is 'Pause Image' (Song Has Not Been Paused), Change It Back To 'Play Image' And Pause Song
    elif play_btn.cget('image') == str(pause_btn_img):
        mixer.music.pause()
        play_btn.configure(image=play_btn_img)


def next_song():
    # Reinitialize 'time_label' And 'time_slider'
    time_label.config(text='--/--')
    time_slider.config(value=0)

    session = DatabaseHandler.session

    # If Playlist Is Not Empty, Run
    # Otherwise Ignore Error
    try:
        # Get Current Song Number
        next_one = playlist_box.curselection()[0]

        # Next Song Number
        next_one = next_one + 1

        # Next Song Title
        song = playlist_box.get(next_one)

        # If Song Is Not The Last One, Run
        # Otherwise Ignore Error
        try:
            # Next Song Location
            global song_location
            song_location = session.query(Song.location).filter_by(title=song).first()[0]

            # Get Song Length
            global song_length
            song_length = mixer.Sound(song_location).get_length()

            # Convert Song Length And Store It
            global converted_song_length
            converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

            # Load And Play Song
            mixer.music.load(song_location)
            mixer.music.play()

            # Clear Active Bar
            playlist_box.select_clear(0, END)
            # Move Active Bar
            playlist_box.activate(next_one)
            # Set Active Bar
            playlist_box.selection_set(next_one, last=None)

            # Change Play Button Image To Pause Image
            play_btn.configure(image=pause_btn_img, command=pause)
        except TypeError:
            pass
    except IndexError:
        pass


def previous_song():
    # Reinitialize 'time_label' And 'time_slider'
    time_label.config(text='--/--')
    time_slider.config(value=0)

    session = DatabaseHandler.session

    # If Playlist Is Not Empty, Run
    # Otherwise Ignore Error
    try:
        # Get Current Song Number
        next_one = playlist_box.curselection()[0]

        # Previous Song Number
        next_one = next_one - 1

        # Previous Song Title
        song = playlist_box.get(next_one)

        # If Song Is Not The First One, Run
        # Otherwise Ignore Error
        try:
            # Previous Song Location
            global song_location
            song_location = session.query(Song.location).filter_by(title=song).first()[0]

            # Get Song Length
            global song_length
            song_length = mixer.Sound(song_location).get_length()

            # Convert Song Length And Store It
            global converted_song_length
            converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

            # Load And Play Song
            mixer.music.load(song_location)
            mixer.music.play()

            # Clear Active Bar
            playlist_box.select_clear(0, END)
            # Move Active Bar
            playlist_box.activate(next_one)
            # Set Active Bar
            playlist_box.selection_set(next_one, last=None)

            # Change Play Button Image To Pause Image
            play_btn.configure(image=pause_btn_img, command=pause)
        except TypeError:
            pass
    except IndexError:
        pass


def stop():
    # Stop Song
    mixer.music.stop()

    # Reinitialize 'Play Button'
    play_btn.configure(image=play_btn_img, command=play)

    # Reinitialize 'time_label' And 'time_slider'
    time_label.config(text='--/--')
    time_slider.config(value=0)


# ----------------------------------------------------------------------------------------------------------------------
# Slider Commands
def set_time(x):
    try:
        # Reload Song And Start From The Point Where Cursor Is Moved
        mixer.music.load(song_location)
        mixer.music.play(start=int(time_slider.get()))
    except NameError:
        time_slider.config(value=0)


def song_time_status():
    # Get Time Left
    current_time = mixer.music.get_pos() / 1000

    # Convert Time Left
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

    if int(time_slider.get()) == int(song_length):
        time_label.config(text=f'{converted_song_length}/{converted_song_length}')
        next_song()
    elif play_btn.cget('image') == str(play_btn_img):
        pass
    elif int(time_slider.get()) == int(current_time):
        # Update Slider Position

        # Display Time Left And Song Length
        time_label.config(text=f'{converted_current_time}/{converted_song_length}')

        time_slider.config(to=int(song_length), value=int(current_time))
    else:
        # Update Slider Position
        time_slider.config(to=int(song_length), value=int(time_slider.get()))

        # Convert New Time
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(time_slider.get())))

        # Display New Time Left
        time_label.config(text=f'{converted_current_time}/{converted_song_length}')

        # Move This By One Second
        next_time = int(time_slider.get()) + 1
        time_slider.config(value=next_time)

    # After 1000ms Call Again song_time_status()
    time_label.after(1000, song_time_status)


def set_volume(x):
    # Set Volume
    mixer.music.set_volume(volume_slider.get())

    # Get Volume Value
    volume = int(mixer.music.get_volume()*100)

    # Display Volume
    display_volume.config(text=volume)


# ----------------------------------------------------------------------------------------------------------------------
# Initialize Window App
window = Tk()
window.config(bg='#262626')
window.geometry('500x350')
window.title('Music Player')
window.iconbitmap('images/icon.ico')

# Initialize Pygame Mixer
mixer.init()

# Create Master Frame
master_frame = Frame(window, bg='#262626')
master_frame.pack(pady=10)

# Create Playlist Name Label
playlist_name = Label(master_frame, text='', bg='#262626', fg='white')
playlist_name.grid(row=0, column=0)

# Create Playlist Box
playlist_box = Listbox(master_frame, width=33, bg='#d9d9d9', borderwidth=0, selectbackground='#6666ff',
                       activestyle='none')
playlist_box.grid(row=1, column=0, pady=10)

# Create Time Slider
time_slider = ttk.Scale(master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, length=200, command=set_time)
time_slider.grid(row=2, column=0)

# Create Time Label
time_label = Label(master_frame, text='--/--', bg='#262626', fg='white')
time_label.grid(row=3, column=0)

# Define Player Buttons Images
play_btn_img = PhotoImage(file='images/play-button.png')
pause_btn_img = PhotoImage(file='images/pause-button.png')
back_btn_img = PhotoImage(file='images/back-button.png')
forward_btn_img = PhotoImage(file='images/forward-button.png')

# Create Player Control Frame
control_frame = Frame(master_frame, bg='#262626')
control_frame.grid(row=4, column=0)

# Create Player Control Buttons
back_btn = Button(control_frame, image=back_btn_img, borderwidth=0, command=previous_song, bg='#262626')
forward_btn = Button(control_frame, image=forward_btn_img, borderwidth=0, command=next_song, bg='#262626')
play_btn = Button(control_frame, image=play_btn_img, borderwidth=0, command=play, bg='#262626')

back_btn.grid(row=0, column=0, padx=10)
play_btn.grid(row=0, column=1, padx=10)
forward_btn.grid(row=0, column=2, padx=10)

# Create Volume Label
volume_label = Label(master_frame, text='Volume', bg='#262626', fg='white')
volume_label.grid(row=0, column=1)

# Create Volume Slider
volume_slider = ttk.Scale(master_frame, from_=1, to=0, orient=VERTICAL, value=1, command=set_volume, length=150)
volume_slider.grid(row=1, column=1, padx=40)
style = ttk.Style()

style.configure('Volume.Vertical.TScale', background='#262626')
volume_slider.config(style='Volume.Vertical.TScale')

style.configure('Time.Horizontal.TScale', background='#262626')
time_slider.config(style='Time.Horizontal.TScale')

# Create Display Volume Label
display_volume = Label(master_frame, text='100', bg='#262626', fg='white')
display_volume.grid(row=2, column=1)

# Create Menu
my_menu = Menu(window)
window.config(menu=my_menu)

# Playlist Menu
playlist_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label='Playlist', menu=playlist_menu)
playlist_menu.add_command(label='Choose Playlist', command=choose_playlist)
playlist_menu.add_command(label='Create Playlist', command=create_playlist)
playlist_menu.add_command(label='Delete Playlist', command=delete_playlist)

# Song Menu
song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label='Song', menu=song_menu)
song_menu.add_command(label='Add Song To Playlist', command=add_song)
song_menu.add_command(label='Remove Song From Playlist', command=remove_song)

# Show Window
window.mainloop()
