from pyrogram import Client

def user_send(path_to_file, book_name):
    client = Client(session_name="mds")
    client.start()
    
    print('Downloading from user to bot')
    client.send_audio('@mds_books_bot', audio=path_to_file, caption=book_name)
    print('Downloading from user to bot DONE')
    
    client.stop()
    
    return 'ok'