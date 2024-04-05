import smtplib
import subprocess
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from configparser import ConfigParser
from email.mime.text import MIMEText
from bitcoinrpc.authproxy import AuthServiceProxy


def check_newblock(): # main application loop
    global lastBlock
    if lastBlock != get_CurrentBlock():
        lastBlock = get_CurrentBlock()
        #print(lastBlock)
        info_labelProgress.config(text="")
        check_transactions()
    else:
        print('same block')
        info_labelCurrentBlock.config(text=str(lastBlock))

    progressStatus = info_labelProgress.cget("text")
    progressStatus = progressStatus + '*'
    info_labelProgress.config(text=progressStatus)

    root.after((connect_interval*1000), check_newblock) # main program logic loop


# function to fetch settings from config file
def get_config_settings():
    config_file = ConfigParser()
    config_file.read('monitor.cfg')

    rpc_user = str(config_file['rpc_credentials']['rpc_user'])
    rpc_pass = str(config_file['rpc_credentials']['rpc_pass'])
    rpc_host = str(config_file['rpc_credentials']['rpc_host'])
    rpc_port = str(config_file['rpc_credentials']['rpc_port'])
    rpc_timeout = str(config_file['rpc_credentials']['rpc_timeout'])
    rpc_interval = str(config_file['rpc_credentials']['rpc_connect_interval'])
    global rpc_list
    rpc_list = [rpc_user, rpc_pass, rpc_host, rpc_port, rpc_timeout, rpc_interval]

    smtp_email = str(config_file['smtp_credentials']['smtp_email'])
    smtp_password = str(config_file['smtp_credentials']['smtp_password'])
    sms_gateway = str(config_file['smtp_credentials']['sms_gateway'])
    smtp_server = str(config_file['smtp_credentials']['smtp_server'])
    smtp_server_port = str(config_file['smtp_credentials']['smtp_server_port'])
    global sms_list
    sms_list = [smtp_email, smtp_password, sms_gateway, smtp_server, smtp_server_port]

    global trans_list
    trans_list = []
    trans_count = 0
    transaction_items = config_file.items("transactions")
    for key, item in transaction_items:
        trans_list.insert(trans_count, item)
        trans_count = trans_count + 1

# Fetch latest confirmed block number
def get_CurrentBlock():
    rpc_client = AuthServiceProxy(f"http://{rpc_list[0]}:{rpc_list[1]}@{rpc_list[2]}:" + rpc_list[3], timeout=int(rpc_list[4]))
    block = rpc_client.getblockcount()
    return block


# Check if transaction outputs have been spent or are currently in mempool
def check_transactions():
    x = 0
    global anySpent
    anySpent = False
    while x < len(trans_list):
        trans_string = trans_list[x]
        transID = trans_string.split(',', -1)
        rpc_client = AuthServiceProxy(f"http://{rpc_list[0]}:{rpc_list[1]}@{rpc_list[2]}:" + rpc_list[3], timeout=int(rpc_list[4]))
        is_utxo_valid = rpc_client.gettxout(transID[0], int(transID[1]))

        if is_utxo_valid:
            pass
            # print('\nValid: ' + transID[2])
        else:
            # print('Not valid' + transID[2])
            send_sms_message(x,transID[2])
            anySpent = True
        x = x + 1

    if anySpent == True:
        message=''
        set_image("images/128x128x.png")
    else:
        message=''
        set_image("images/128x128.png")
    info_label_message.config(text=str(message))


def set_image(myImage):
    global img
    img = ImageTk.PhotoImage(Image.open(myImage))
    labelImage = ttk.Label(root, image=img)
    labelImage.place(x=100, y=275)


def open_config_file():
    subprocess.call(['open', '-a', 'TextEdit', 'monitor.cfg'])


def send_sms_message(number, wallet):
    try:
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = sms_list[0]
        msg['To'] = sms_list[2]
        msg['Subject'] = "  UTXO Spent from " + str(wallet)  + "\n"
        message = "trans_" + str(number+1) + "\n"

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(sms_list[3], int(sms_list[4]))
        server.starttls()
        server.login(sms_list[0], sms_list[1])
        server.sendmail(sms_list[0], sms_list[2], msg.as_string())
        server.quit()
    except:
        print("There was an error sending your message.")
        #rpc_label_message = ttk.Label(root, text="There was an error sending your message.  Please check your settings.", font=("Helvetica 13 bold"))
        #rpc_label_message.place(x=100, y=250)
    else:
        print("Test message sent successfully")
        #rpc_label_message = ttk.Label(root, text="Test message sent successfully", font=("Helvetica 13 bold"))
        #rpc_label_message.place(x=100, y=250)


def restart():
    get_config_settings()
    connect_interval = int(rpc_list[5])
    startBlock = get_CurrentBlock()
    lastBlock = startBlock
    info_labelProgress.config(text="")
    labelInterval.config(text=str(connect_interval) + " sec")
    check_transactions()
    check_newblock()



# Create the main window
root = tk.Tk()
root.title("Monitor")
root.title("UTXO Monitor for Mac")
root.geometry("700x500")
root.resizable(width=False, height=False)

# run starting processes to initialize the app
get_config_settings()
connect_interval = int(rpc_list[5])
startBlock = get_CurrentBlock()
lastBlock = startBlock

# add labels, text and buttons to root
info_labelTitle = ttk.Label(root, text="General Monitoring Information", font=("Helvetica 13 bold"))
info_labelTitle.place(x=40, y=20)

info_labelVersion = ttk.Label(root, text="Monitor Version:", font=("Helvetica 13"))
info_labelVersion.place(x=40, y=50)
labelVersion = ttk.Label(root, text="v1.0", font=("Helvetica 13"))
labelVersion.place(x=200, y=50)

info_labelContactNumber = ttk.Label(root, text="SMS Number:", font=("Helvetica 13"))
info_labelContactNumber.place(x=40, y=80)
labelContactNumber = ttk.Label(root, text=sms_list[2][:10], font=("Helvetica 13"))
labelContactNumber.place(x=200, y=80)

info_labelTransCount = ttk.Label(root, text="Transactions Monitoring:", font=("Helvetica 13"))
info_labelTransCount.place(x=40, y=110)
labelTransCount = ttk.Label(root, text=len(trans_list), font=("Helvetica 13"))
labelTransCount.place(x=200, y=110)

info_labelInterval = ttk.Label(root, text="Monitoring Interval:", font=("Helvetica 13"))
info_labelInterval.place(x=40, y=140)
labelInterval = ttk.Label(root, text=str(connect_interval) + " sec", font=("Helvetica 13"))
labelInterval.place(x=200, y=140)

info_labelStartBlock = ttk.Label(root, text="Starting Block:", font=("Helvetica 13"))
info_labelStartBlock.place(x=40, y=170)
labelStartBlock = ttk.Label(root, text=startBlock, font=("Helvetica 13"))
labelStartBlock.place(x=200, y=170)

info_labelCurrentBlock = ttk.Label(root, text="Current Block:", font=("Helvetica 13"))
info_labelCurrentBlock.place(x=40, y=200)
info_labelCurrentBlock = ttk.Label(root, text=lastBlock, font=("Helvetica 13"))
info_labelCurrentBlock.place(x=200, y=200)

# Add RPC labels
rpc_labelTitle = ttk.Label(root, text="RPC Information", font=("Helvetica 13 bold"))
rpc_labelTitle.place(x=375, y=20)

rpc_labelUser = ttk.Label(root, text="User Name: ", font=("Helvetica 13"))
rpc_labelUser.place(x=375, y=50)
rpc_entryUser = ttk.Label(root, text=rpc_list[0], font=("Helvetica 13"), justify="left", width=43)
rpc_entryUser.place(x=455, y=50)

rpc_labelPassword = ttk.Label(root, text="Password: ", font=("Helvetica 13"))
rpc_labelPassword.place(x=375, y=80)
rpc_entryPassword = ttk.Label(root, text=rpc_list[1],  font=("Helvetica 13"), justify="left", width=43)
rpc_entryPassword.place(x=455, y=80)

rpc_labelHost = ttk.Label(root, text="Host: ", font=("Helvetica 13"))
rpc_labelHost.place(x=375, y=110)
rpc_entryHost= ttk.Label(root, text=rpc_list[2],  font=("Helvetica 13"), justify="left", width=43)
rpc_entryHost.place(x=455, y=110)

rpc_labelPort = ttk.Label(root, text="Port: ", font=("Helvetica 13"))
rpc_labelPort.place(x=375, y=140)
rpc_entryPort= ttk.Label(root, text=rpc_list[3],  font=("Helvetica 13"), justify="left", width=43)
rpc_entryPort.place(x=455, y=140)

rpc_labelTimeout = ttk.Label(root, text="Timeout: ", font=("Helvetica 13"))
rpc_labelTimeout.place(x=375, y=170)
rpc_entryTimeout= ttk.Label(root, text=rpc_list[4],  font=("Helvetica 13"), justify="left", width=43)
rpc_entryTimeout.place(x=455, y=170)

# add SMS labels
sms_labelTitle = ttk.Label(root, text="SMS Information", font=("Helvetica 13 bold"))
sms_labelTitle.place(x=375, y=225)

sms_labelEmail = ttk.Label(root, text="SMTP Email: ", font=("Helvetica 13"))
sms_labelEmail.place(x=375, y=255)
sms_entryEmail = ttk.Label(root, text=sms_list[0], font=("Helvetica 13"), justify="left", width=43)
sms_entryEmail.place(x=485, y=255)

sms_labelPassword = ttk.Label(root, text="SMTP Password: ", font=("Helvetica 13"))
sms_labelPassword.place(x=375, y=281)
sms_entryPassword = ttk.Label(root, text=sms_list[1], font=("Helvetica 13"), justify="left", width=43)
sms_entryPassword.place(x=485, y=281)

sms_labelServer = ttk.Label(root, text="SMTP Server: ", font=("Helvetica 13"))
sms_labelServer.place(x=375, y=312)
sms_entryServer= ttk.Label(root, text=sms_list[3], font=("Helvetica 13"), justify="left", width=43)
sms_entryServer.place(x=485, y=312)

sms_labelPort = ttk.Label(root, text="SMTP Port: ", font=("Helvetica 13"))
sms_labelPort.place(x=375, y=343)
sms_entryPort= ttk.Label(root, text=sms_list[4], font=("Helvetica 13"), justify="left", width=43)
sms_entryPort.place(x=485, y=343)

sms_labelGateway = ttk.Label(root, text="SMS Gateway: ", font=("Helvetica 13"))
sms_labelGateway.place(x=375, y=370)
sms_entryGateway= ttk.Label(root, text=sms_list[2], font=("Helvetica 13"), justify="left", width=43)
sms_entryGateway.place(x=485, y=370)

info_label_message = ttk.Label(root, text="sfdgsdfgs", font=("Helvetica 15 bold"))
info_label_message.place(x=10, y=400)

info_labelProgress = tk.Label(root,text='', font=("Helvetica 10"), wraplength=600, justify="left")
info_labelProgress.place(x=10, y=470)

restartButton = ttk.Button(root, text="Restart Monitor", width=15, command=restart)
restartButton.place(x=85, y=230)

cfgButton = ttk.Button(root, text="Edit .cfg", width=10, command=open_config_file)
cfgButton.place(x=425, y=400)


# Initial transaction check when program starts
check_transactions()
# Start checking for a new block
check_newblock() # main application logic loop
# Start the Tkinter event loop
root.mainloop()