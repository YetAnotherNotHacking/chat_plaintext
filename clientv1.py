import socket
import threading
import PySimpleGUI as sg

class Client:
    def __init__(self, host='127.0.0.1', port=45685):
        self.nickname = ''

        # Set up the GUI layout
        layout = [
            [sg.Text("Enter your nickname: "), sg.Input(key='-NICKNAME-')],
            [sg.Multiline(size=(60, 20), key='-MESSAGE-')],
            [sg.Button('Send'), sg.Button('Exit')]
        ]

        self.window = sg.Window('Chat Platform', layout)

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    print(message)
            except:
                print("An error occurred!")
                self.client.close()
                break

    def write(self, message):
        message = f'{self.nickname}: {message}'
        self.client.send(message.encode('ascii'))

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                self.client.close()
                break

            if event == 'Send':
                self.nickname = values['-NICKNAME-']
                if not self.nickname:
                    sg.popup_error('Please enter a nickname.')
                else:
                    self.client.send('NICK'.encode('ascii'))
                    self.client.send(self.nickname.encode('ascii'))
                    message = values["-MESSAGE-"].strip()
                    if message:
                        self.write(message)
                        self.window['-MESSAGE-'].update('')  # Clear the input field

# Create the client instance
client = Client()
client.start()

# Close the PySimpleGUI window
client.window.close()
