import socket
import threading
from datetime import datetime
import time
import csv
import pandas as pd
import hashlib
import string


host = "localhost"
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

server.listen()

clients = []
nicknames = []

dataset = []
form = []

private_chats = []

clients__pr = {}
buffer = []


def check_username(name):
    every = string.printable[:-6]
    for letter in name:
        if letter not in every:
            return False
    return True


def check_hash(hashed, string):
    salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
    dataBase_password = string + salt
    hashed2 = hashlib.sha256(dataBase_password.encode())
    if hashed == hashed2:
        return True
    return False


def hash_pwd(password):
    salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
    dataBase_password = password + salt
    hashed = hashlib.sha256(dataBase_password.encode())
    return hashed.hexdigest()


def replace_value(old_value, new_value, column_name):
    df = pd.read_csv('database.csv')
    df.loc[df[column_name] == old_value, column_name] = new_value
    df.to_csv('database.csv', index=False)


def check_username_exist(value):
    with open('database.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['username'] == value:
                return True
        return False


def is_group_owner(value, group_name):
    with open('group_db.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['group_admin'] == value and row["group_name"] == group_name:
                return True
        return False


def check_group_name_exists(value):
    print(value)
    with open('group_db.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            print(row["group_name"])
            if row['group_name'] == value:
                return True
        return False


def check_id_exist(value):
    with open('database.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['id'] == value:
                return True
        return False


def get_id(username):
    with open('database.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['username'] == username:
                return row['id']
    return None


def get_username(idd):
    with open('database.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['id'] == idd:
                return row['username']
    return None


def get_password(username):
    with open('database.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        for row in data:
            if row['username'] == username:
                return row['password']
    return None


def get_public(idd):
    try:
        with open(f"public_{idd}.txt", "rb") as file:
            return file.read()
    except:
        return None


def broadcast(message, client):
    try:
        group_id = None
        for item in dataset:
            if item["client"] == client:
                group_id = item["group"]
        if group_id is None:
            print("User not in list")
            pass
        else:
            members = []
            for item in dataset:
                if item["group"] == group_id:
                    members.append(item["client"])
            print(message)
            for person in members:
                if person != client:
                    person.send(message)

    except KeyboardInterrupt:
        pass


def broadcast_file(name, client, data, sender):
    try:
        print("okay")
        group_id = None
        for item in dataset:
            if item["client"] == client:
                group_id = item["group"]
        if group_id is None:
            print("User not in list")
            pass
        else:
            members = []
            for item in dataset:
                if item["group"] == group_id:
                    members.append(item["client"])
            print("sending file")
            for person in members:
                if person != client:
                    person.send("FILE_INCOMING".encode())
                    time.sleep(.5)
                    person.send(f"{name}".encode())
                    time.sleep(.5)
                    person.send(sender.encode())
                    person.send(data.encode())
                    person.send("DONE:::".encode())

    except KeyboardInterrupt:
        pass


def broadcast_image(name, client, data, sender, final):
    try:
        if not final:
            print("okayx2")
            group_id = None
            for item in dataset:
                if item["client"] == client:
                    group_id = item["group"]
            if group_id is None:
                print("User not in list")
                pass
            else:
                members = []
                for item in dataset:
                    if item["group"] == group_id:
                        members.append(item["client"])
                print("sending image")
                for person in members:
                    if person != client:
                        person.send(f"{name}".encode())
                        time.sleep(.5)
                        person.send(sender.encode())
                        time.sleep(.5)
                        person.send(data)

        else:
            print("okayx3")
            group_id = None
            for item in dataset:
                if item["client"] == client:
                    group_id = item["group"]
            if group_id is None:
                print("User not in list")
                pass
            else:
                members = []
                for item in dataset:
                    if item["group"] == group_id:
                        members.append(item["client"])
                print("sending final message")
                for person in members:
                    person.send("DONE:::".encode())

    except KeyboardInterrupt:
        pass


def handle(client, g_id):
    dataset.append({"client": client, "group": g_id})
    while True:
        try:
            pp = False
            message = client.recv(1024)

            if message == b'':
                pp = True
                pass
            elif message.decode() == "FILE:::::":
                # TODO: add try-except everywhere
                pp = True
                filename = client.recv(1024).decode()
                sender = client.recv(1024).decode()

                al = []

                while True:
                    more_data = client.recv(1024).decode()
                    if more_data.endswith(":"):
                        more_data = more_data[:-5]
                        al.append(more_data)
                        break
                    else:
                        al.append(more_data)
                    # print(more_data)
                complete_data = "".join(al)
                print("Data received.")
                print(complete_data)

                broadcast_file(name=filename, client=client, data=complete_data, sender=sender)
            elif message.decode() == "IMAGE:::::":
                pp = True
                filename = client.recv(1024)
                sender = client.recv(1024)

                print("okay")
                members = []
                group_id = None
                for item in dataset:
                    if item["client"] == client:
                        group_id = item["group"]
                if group_id is None:
                    print("User not in list")
                    pass
                else:
                    members = []
                    for item in dataset:
                        if item["group"] == group_id:
                            members.append(item["client"])
                    print("sending file")

                print(members)

                for person in members:
                    if person != client:
                        person.send(b"IMAGE_INCOMING")
                        time.sleep(.5)
                        print("sent first")
                        person.send(filename + b"<<MARKER>>" + sender)
                        time.sleep(.5)

                while True:
                    data = client.recv(1024)
                    print("data:", data)
                    if data == b":ENDED:":
                        for person in members:
                            if person != client:
                                person.send(b":ENDED:")
                        break
                    if not data:
                        for person in members:
                            if person != client:
                                person.send(b":ENDED:")
                        break
                    if data.endswith(b":ENDED:"):
                        for person in members:
                            if person != client:
                                person.sendall(data.split(b":ENDED:")[0])
                                time.sleep(.5)
                                person.sendall(b":ENDED:")
                        break

                    for person in members:
                        if person != client:
                            person.sendall(data)
                print("done")

            if not pp:
                if message.decode() == "PRIV:":
                    print("okay")
                print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Message: ", message)
                if ": " in message.decode():
                    broadcast(message, client)
        except ConnectionResetError:
            try:
                s = False
                for item in form:
                    if item["client"] == client:
                        print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {item['name']} disconnected.")
                        members = []
                        for item2 in dataset:
                            if item2["group"] == g_id:
                                members.append(item2["client"])
                        for person in members:
                            person.send(f":NEW_LEAVE::{item['name']}")
                        s = True
                if not s:
                    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Unknown client disconnected.")
                clients.remove(client)
                for item in dataset:
                    if item["client"] == client:
                        dataset.remove(item)
            except Exception as e:
                print(e)
                clients.remove(client)
                print("Client disconnected x2")
            break
        except KeyboardInterrupt:
            print("Ctrl+C detected")
            break
        except OSError:
            pass
    exit("ok")


def handle_client_while(client, p):
    while True:
        try:
            request = client.recv(1024)
            message = client.recv(1024)
            print("Request: ", request)
            print("Message:", message)
            # print("P:", p)
            request = request.decode()
            if request.startswith("/pm"):
                _, idd = request.split(" ")
                send_message(idd, message, p, buf=False)
            else:
                print("Invalid.")
                client.close()
            clients__pr[p] = client

        except Exception as e:
            print(e)
            print("client disconnected.")
            break


def handle_client(client, _, oho):
    if oho == "True":
        p = client.recv(1024).decode()
        print(p)
        clients__pr[p] = client
        dd = p
    else:
        clients__pr[oho] = client
        dd = oho
    p = dd
    for item in buffer:
        if item["from"] == p:
            print("yws")
            print("FROM:", item["from"])
            send_message(item["from"], item["mess"], p, buf=True)
            buffer.remove(item)
    threading.Thread(target=handle_client_while, args=(client, p,)).start()


def send_message(idd, message, p, buf=True):
    print(idd, message, p)
    if buf:
        try:
            """
            recipient_socket = clients__pr[idd]
            recipient_socket.send(f"INCOMING:{p}|||".encode())
            print("okay")
            recipient_socket.send(message)
            print("sent")
            """
            recipient_socket = clients__pr[idd]
            print(idd)
            recipient_socket.send(f"INCOMING:{p}|||".encode())
            print("waiting")
            time.sleep(1)
            recipient_socket.send(message)
        except:
            buffer.append({"from": idd, "to": p, "mess": message})
            print("Sender not available.")
    else:
        idd = get_username(idd) + "#" + idd
        try:
            recipient_socket = clients__pr[idd]
            print(idd)
            recipient_socket.send(f"{p}---".encode())
            print("waiting x2")
            time.sleep(1)
            recipient_socket.send(message)
        except Exception as e:
            print(e)
            buffer.append({"from": idd, "to": p, "mess": message})
            print("Sender not available.")


def fuck_around(client, address):
    try:
        xxx = client.recv(1024).decode()

        print("X", xxx)
        if xxx == "PRIV:":
            print("private")
            oho = "True"
            client_thread = threading.Thread(target=handle_client, args=(client, address, oho,))
            client_thread.start()
        elif xxx.startswith("SIGNUP:::"):
            print("ye")
            _, username, pas, idd = xxx.split(":::")
            public_key = client.recv(1024).decode()

            if len(username) > 10 or " " in username or not check_username(username):
                client.send(b"errorv3")

            print(username, pas, idd)
            if check_username_exist(username):
                client.send(b"error")
            else:
                if check_id_exist(idd):
                    client.send(b"errorv2")
                else:
                    with open("database.csv", "a") as data_file_:
                        data_file_.write(f"{username},{pas},{idd}\n")
                    with open(f"public_{idd}.txt", "w") as file:
                        file.write(public_key)
                    client.send("success".encode())
        elif xxx.startswith("LOGIN:::"):
            _, username, password = xxx.split(":::")
            print(username, password)
            if not check_username_exist(username):
                client.send("error".encode())
            else:
                pas = get_password(username)
                if pas == password:
                    client.send(f"success:{get_id(username)}".encode())
                else:
                    client.send("errorv2".encode())
        elif xxx.startswith("CHANGE_USERNAME:"):
            _, username, password, new_username = xxx.split(":")
            if check_username_exist(username):
                pas = get_password(username)
                if pas == password:
                    replace_value(username, new_username, "username")
                    client.send(b"success")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("CHANGE_PASSWORD:"):
            _, old, new, username = xxx.split(":")
            if check_username_exist(username):
                pas = get_password(username)
                if pas == new:
                    replace_value(get_password(username), hash_pwd(new), "password")
                    client.send(b"success")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("DELETE_ALL:"):
            _, username, password = xxx.split(":")
            if check_username_exist(username):
                pas = get_password(username)
                if pas == password:
                    df = pd.read_csv('database.csv')
                    fieldname = 'username'
                    value_to_delete = username
                    df = df[df[fieldname] != value_to_delete]
                    df.to_csv('database.csv', index=False)
                    client.send(b"success")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("PRIV:"):
            try:
                _, idd = xxx.split(":")
                print("private")
                client_thread = threading.Thread(target=handle_client, args=(client, address, idd,))
                client_thread.start()
            except Exception:
                print("da fuck")
                pass
        elif xxx.startswith("GET_PUBLIC:"):
            idd = xxx.split(":")[1]
            if check_id_exist(idd):
                print("Ok")
                aa = get_public(idd)
                if aa:
                    client.send(aa)
                else:
                    client.send(b"error")
            else:
                print("nah")
                client.send(b"error")
        elif xxx.startswith("GET_USERNAME:"):
            idd = xxx.split(":")[1]
            if check_id_exist(idd):
                aa = get_username(idd)
                if aa:
                    client.send(aa.encode())
                else:
                    client.send(b"error")
            else:
                print("nah")
                client.send(b"error")
        elif xxx.startswith("USER_EXISTS:"):
            u = xxx.split(":")[1]
            if check_username_exist(u):
                client.send(b"exists")
            else:
                client.send(b"not exist")
        elif xxx.startswith("START_VOICE:"):
            print("VOICE REQUEST RECEIVED.")
            threading.Thread(target=start_voice, args=(client,))
        elif xxx.startswith("CREATE_GROUP:"):
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    client.send(b"group_exists")
                else:
                    with open("group_db.csv", "a") as g_gile:
                        g_gile.write(f"{group_name},{username}\n")
                    client.send(b"success")
            else:
                client.send(b"error")
        elif xxx.startswith("VALID_GROUP_NAME:"):
            _, g_name = xxx.split(":")
            if check_group_name_exists(g_name):
                client.send(b"yes")
            else:
                client.send(b"error")
        elif xxx.startswith("DELETE_GROUP:"):
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    if is_group_owner(username, group_name):
                        df = pd.read_csv('group_db.csv')
                        fieldname = 'group_name'
                        df = df[df[fieldname] != group_name]
                        df.to_csv('group_db.csv', index=False)
                        client.send(b"success")
                        # TODO: Send signal to everyone to delete group
                        members = []
                        for item in dataset:
                            if item["group"] == group_name:
                                members.append(item["client"])
                        for person in members:
                            if person != client:
                                person.send(b"::GROUP_DELETION_INITIATED::")
                    else:
                        client.send(b"error")
                else:
                    client.send(b"error")
        elif xxx.startswith("RENAME_GROUP:"):
            _, group_name, new_group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    if is_group_owner(username, group_name):
                        dataframe = pd.read_csv("group_db.csv")
                        dataframe.replace(
                            to_replace=group_name,
                            value=new_group_name,
                            inplace=True
                        )
                        dataframe.to_csv("group_db.csv", index=False)
                        client.send(b"success")
                        # TODO: Send signal to everyone to rename group
                        members = []
                        for item in dataset:
                            if item["group"] == group_name:
                                members.append(item["client"])
                        for person in members:
                            if person != client:
                                person.send(f"::RENAME_OF_GROUP:::{new_group_name}".encode())
                    else:
                        client.send(b"error")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")

        else:
            if xxx.startswith("ID:::::"):
                _, nickname, group_id = xxx.split("|||")
                nicknames.append(nickname)

                clients.append(client)
                form.append({"client": client, "name": nickname})

                print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {nickname} joined.")

                members = []
                for item in dataset:
                    if item["group"] == group_id:
                        members.append(item["client"])
                for person in members:
                    person.send(f":NEW_JOIN::{nickname}")

                thread = threading.Thread(target=handle, args=(client, group_id,))
                thread.start()
    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Error: {e}")


########### VOICE CHAT ###########
clients_voice = []
dataset_voice = []


def handle_client_voice(sock, reci):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("nah")
                break

            for item in dataset:
                if item["name"] == reci:
                    item["client"].sendall(data)
        except:
            print("break 1")
            sock.close()
            break
    print("break 2")


def start_voice(client_socket):
    nickname = client_socket.recv(1024).decode()

    for item in dataset:
        if item["name"] == nickname:
            dataset.remove(item)

    rec = client_socket.recv(1024).decode()

    print(f"{nickname} calls {rec}")

    dataset.append({"client": client_socket, "name": nickname})

    # add the client socket to the list
    clients.append(client_socket)

    # handle the client connection in a new thread
    client_thread = threading.Thread(target=handle_client_voice, args=(client_socket, rec,))
    client_thread.start()


def receive():
    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Server started...")
    while True:
        try:
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            threading.Thread(target=fuck_around, args=(client, address,)).start()

        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(e)
            print("Client disconnected.")


receive()
