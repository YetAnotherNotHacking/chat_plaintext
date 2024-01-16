import socket
import threading
import PySimpleGUI as sg

class Client:
    def __init__(self, host='127.0.0.1', port=45685):
        self.nickname = ''
        self.channel = ''
        self.channels = []

        # Get nickname from user
        self.get_nickname()

        # Set up the GUI layout
        self.layout = [
            [sg.Text(f'Nickname: {self.nickname}', key='-NICKNAME-', size=(20, 1)),
             sg.Button('Change Nickname')],
            [sg.Listbox(values=self.channels, size=(20, 10), key='-CHANNELS-'),
             sg.Multiline(size=(60, 20), key='-MESSAGES-')],
            [sg.Input(key='-MESSAGE-', size=(40, 1)), sg.Button('Send'), sg.Button('Exit')]
        ]

        self.window = sg.Window('Chat Platform', self.layout)

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        # Send the nickname to the server
        self.client.send('NICK'.encode('ascii'))
        self.client.send(self.nickname.encode('ascii'))

        # Request the list of channels from the server
        self.client.send('LIST_CHANNELS'.encode('ascii'))

    def get_nickname(self):
        while True:
            self.nickname = sg.popup_get_text('Enter your nickname:')
            if self.nickname:
                break

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message.startswith('NICK'):
                    # Update nickname in the GUI
                    new_nickname = message.split(':')[1].strip()
                    self.nickname = new_nickname
                    self.window['-NICKNAME-'].update(f'Nickname: {self.nickname}')
                else:
                    print(message)
            except:
                print("An error occurred!")
                self.client.close()
                break

    def write(self, message):
        full_message = f'{self.channel}: {message}'
        self.client.send(full_message.encode('ascii'))

    def list_channels(self):
        self.client.send('LIST_CHANNELS'.encode('ascii'))

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                self.client.close()
                break

            if event == 'Send':
                message = values["-MESSAGE-"].strip()
                if message:
                    self.write(message)
                    self.window['-MESSAGE-'].update('')  # Clear the input field

            if event == 'Change Nickname':
                self.get_nickname()
                self.client.send(f'NICK:{self.nickname}'.encode('ascii'))

            if event == '-CHANNELS-':
                selected_channel = values['-CHANNELS-'][0]
                if selected_channel != self.channel:
                    self.channel = selected_channel
                    sg.popup(f'Switched to channel: {self.channel}')

            if event == 'LIST_CHANNELS':
                self.list_channels()

# Create the client instance
client = Client()
client.start()

# Close the PySimpleGUI window
client.window.close()
