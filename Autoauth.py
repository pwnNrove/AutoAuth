#Step 1: Check if VPN is active
#Step 2: Check if login is required
#Step 3: If login is required, Read config file
#Step 4: If config file is not found, or not in proper JSON format, then create a new file
#Step 5: Check if login is successful

#Automatically login to the college network
#If VPN is active, it will not work in some cases
#Add '172.15.15.1' in 'Exclude split tunnel' list to avoid any connection error during authentication

import requests
import json
import time

def start_warnings():
    if is_cloudflare():
        print("[*] CAUTION: Cloudflare detected !!!")

    print("[*] Read following points:")
    print("\t1. I am not responsible for any damage caused by this script")
    print("\t2. If VPN is active, it will not work in some cases")
    print("\t3. Add '172.15.15.1' in 'Exclude split tunnel' list to avoid error during authentication")
    print("\t4. If you are using a proxy, you `might` need to disable it temporarily")
    print("\n[*] I can handle few exceptions, but not all")

    print("\n[*] If you read the above points , press 'y' to continue")
    if input() != 'y':
            return False
    else:
        print("Continuing with Autoauth...")
        return True

def is_cloudflare(): # Step 1: Check if VPN is active
    try:
        response = requests.get(url="http://ipinfo.io/json")
        if 'Cloudflare' in response.text:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        print("[-] Error in checking VPN status")
        print("[*] Response size: "+str(response.status_code))
        print("[*] Most probably you are not logged in...")
        login()
        return False

def is_login_required(detect_url): # Step 2: Check if login is required
    try:
        response = requests.get(detect_url)
        return response.status_code != 204
    except requests.exceptions.RequestException:
        print("Error in checking login status")
        return False

def create_config():
    print("Creating config file...")
    ui = input("Enter your username: ")
    passw = input("Enter your password: ")
    timeout = input("Enter timeout (in seconds): ")
    with open("autoauth.config", "w") as json_file:
        data = {
            "ui": ui,
            "passw": passw,
            "timeout": timeout
        }
        json.dump(data, json_file)
    json_file.close()
    read_config()

def read_config():
    global ui, passw, timeout
    try:
        with open('autoauth.config', "r") as json_file:
            data = json.load(json_file)
            ui = data['ui']
            passw = data['passw']
            timeout = data['timeout']
            return True
    except FileNotFoundError:
        print("[-] Config file not found")
        create_config()
        return True
    except NameError:
        print("[-] Config file os not in proper format")
        create_config()
        return True
    except:
        print("Error in reading config file")
        return False


def login(): # Step 5: Check if login is successful
    tar_url = "http://172.15.15.1:1000/login?="
    try:
        response = requests.get(url=tar_url).text
        for line in response.splitlines():
            if "magic" in line:
                magic_=line.split('value=')[1].replace('"', '').replace('>','')
                break

        data = {'username':ui,
                'password':passw,
                'magic':magic_,
                '4Tredir':"'"
                }

        r = requests.post(url = tar_url, data = data)
        if 'Authentication Keepalive' in r.text:
            print('Done...')
            return True
        else: 
            print('Wrong Password')
            return False

    except requests.exceptions.RequestException:
        print("Connection Error")
        return False


#__main__
def main():
    if not start_warnings():
            return
    while True:
        try:
            if is_cloudflare():
                print("[*] Cloudflare detected")
            else:
                print("[*] Cloudflare not detected")
            if read_config():
                print("[+] Config file loaded")
            else:
                print("[-] Error in reading config file")
                print("[*] Creating new config file...")
                create_config()
            if is_login_required("http://cloudflareportal.com/test"):
                print("[***] Login is required")
                if login():
                    print("[*] Sleeping for " + str(timeout) + " seconds")
                    time.sleep(int(timeout))
                else:
                    return False
            else:
                print("\n[*] Login not required...")
                print("[*] Sleeping for " + str(timeout) + " seconds")
                time.sleep(int(timeout))
                print("\n")
                continue
                
        except KeyboardInterrupt:
            print("Exiting...")
            return
        except NameError:
            create_config()
        except Exception as e:
            print("Error: " + e)
            print("Make sure you are connected to the college network and VPN/proxy is disabled")
            print("If done, press 'y' to continue")
            if input() != 'y':
                return
            print("Checking again in " + str(timeout) + " seconds")
            print("Waiting for next check...")
            time.sleep(int(timeout))

if __name__ == "__main__":
    main()

#Generate a .exe file using pyinstaller
#pyinstaller --onefile --noconsole Autoauth.py
