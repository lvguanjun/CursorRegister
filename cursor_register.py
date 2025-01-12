import argparse
import concurrent.futures
import csv
import os
import re
import csv
import copy
import argparse
import threading
import concurrent.futures
from datetime import datetime

from DrissionPage import Chromium, ChromiumOptions
from faker import Faker
from DrissionPage import ChromiumOptions, Chromium
from temp_mails import Tempmail_io

CURSOR_URL = "https://www.cursor.com/"
CURSOR_LOGIN_URL = "https://authenticator.cursor.sh"
CURSOR_SIGN_UP_URL = "https://authenticator.cursor.sh/sign-up"
CURSOR_SETTINGS_URL = "https://www.cursor.com/settings"

hide_account_info = os.getenv('HIDE_ACCOUNT_INFO', 'false').lower() == 'true'
enable_register_log = True

def cursor_turnstile(tab, retry_times = 5):
    for retry in range(retry_times): # Retry times
        try:
            if enable_register_log: print(f"[Register][{retry}] Passing Turnstile")
            challenge_shadow_root = tab.ele('@id=cf-turnstile').child().shadow_root
            challenge_shadow_button = challenge_shadow_root.ele("tag:iframe", timeout=30).ele("tag:body").sr("xpath=//input[@type='checkbox']")
            if challenge_shadow_button:
                challenge_shadow_button.click()
                tab.wait.load_start()
                break
        except:
            pass
        if retry == retry_times - 1:
            print("[Register] Timeout when passing turnstile")

def sign_up(options):

    # Maybe fail to open the browser
    try:
        browser = Chromium(options)
    except Exception as e:
        print(e)
        return None

    retry_times = 5

    # Thread id for debug info
    thread_id = threading.current_thread().ident
    
    # Get temp email address
    mail = Tempmail_io()
    email = mail.email

    # Get password and name by faker
    fake = Faker()
    password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    first_name, last_name = fake.name().split(" ")[0:2]

    tab = browser.new_tab(CURSOR_SIGN_UP_URL)
    browser.wait(0.5, 1.5)
    # Input first name, last name, email
    for retry in range(retry_times):
        try:
            if enable_register_log: print(f"[Register][{thread_id}][{retry}] Input first name, last name, email")
            tab.ele("xpath=//input[@name='first_name']").input(first_name, clear=True)
            tab.ele("xpath=//input[@name='last_name']").input(last_name, clear=True)
            tab.ele("xpath=//input[@name='email']").input(email, clear=True)
            tab.ele("@type=submit").click()
            tab.wait(0.5, 2.5)
            tab.wait.load_start()

            if tab.ele("xpath=//input[@name='email']").attr("data-invalid") == "true":
                print(f"[Register][{thread_id}] Email is invalid")
                return None

            # If not in password page, try pass turnstile page
            if not tab.wait.eles_loaded("xpath=//input[@name='password']", timeout=3) and tab.ele("xpath=//input[@name='email']").attr("data-valid") is not None:
                if enable_register_log: print(f"[Register][{thread_id}][{retry}] Try pass Turnstile for email page")
                cursor_turnstile(tab)

        except Exception as e:
            print(f"[Register][{thread_id}] Exception when handlding email page.")
            print(e)

        # In password page or data is validated, continue to next page
        if tab.wait.eles_loaded("xpath=//input[@name='password']"):
            print(f"[Register][{thread_id}] Continue to password page")
            break

        # Kill the function since time out 
        if retry == retry_times - 1:
            print(f"[Register][{thread_id}] Timeout when inputing email address")
            return None
    
    # Input password
    for retry in range(retry_times):
        try:
            if enable_register_log: print(f"[Register][{thread_id}][{retry}] Input password")
            tab.ele("xpath=//input[@name='password']").input(password, clear=True)
            tab.ele('@type=submit').click()
            tab.wait(1.5, 2.5)
            tab.wait.load_start()
            
            if tab.ele("xpath=//input[@name='password']").attr("data-invalid") == "true":
                print(f"[Register][{thread_id}] Pssword is invalid")
                return None

            # If not in verification code page, try pass turnstile page
            if not tab.wait.eles_loaded("xpath=//input[@data-index=0]", timeout=3) and tab.ele("xpath=//input[@name='password']").attr("data-valid") is not None:
                if enable_register_log: print(f"[Register][{thread_id}][{retry}] Try pass Turnstile for password page")
                cursor_turnstile(tab)

        except Exception as e:
            print(f"[Register][{thread_id}] Exception when handling password page.")
            print(e)
                
        # In code verification page or data is validated, continue to next page
        if tab.wait.eles_loaded("xpath=//input[@data-index=0]"):
            print(f"[Register][{thread_id}] Continue to email code page")
            break

        # Kill the function since time out 
        if retry == retry_times - 1:
            if enable_register_log: print(f"[Register][{thread_id}] Timeout when inputing password")
            return None

    # Get email verification code
    try:
        data = mail.wait_for_new_email(delay=1.0, timeout=120)
        body_text = data["body_text"]
        message_text = body_text.strip().replace('\n', '').replace('\r', '').replace('=', '')
        verify_code = re.search(r'open browser window\.(\d{6})This code expires', message_text).group(1)
    except Exception as e:
        print(f"[Register][{thread_id}] Fail to get code from email. Email data: {data}")
        return None
    
    # Input email verification code
    for retry in range(retry_times):
        try:
            if enable_register_log: print(f"[Register][{thread_id}][{retry}] Input email verification code")

            for idx, digit in enumerate(verify_code, start = 0):
                tab.ele(f"xpath=//input[@data-index={idx}]", timeout=30).input(digit, clear=True)
                tab.wait(0.1, 0.3)
            tab.wait(0.5, 1.5)
        except Exception as e:
            print(f"[Register][{thread_id}] Exception when handling email code page.")
            print(e)

        if tab.url != CURSOR_URL:
            if enable_register_log: print(f"[Register][{thread_id}][{retry}] Try pass Turnstile for email code page.")
            cursor_turnstile(tab)

        if tab.wait.url_change(CURSOR_URL, timeout=180):
            break

        # Kill the function since time out 
        if retry == retry_times - 1:
            if enable_register_log: print(f"[Register][{thread_id}] Timeout when inputing email verification code")
            return None

    # Get cookie
    cookies = tab.cookies().as_dict()
    token = cookies.get('WorkosCursorSessionToken', None)
    if enable_register_log:
        if token is not None:
            print(f"[Register][{thread_id}] Register Account Successfully.")
        else:
            print(f"[Register][{thread_id}] Register Account Failed.")

    if not hide_account_info:
        print(f"[Register] Cursor Email: {email}")
        print(f"[Register] Cursor Password: {password}")
        print(f"[Register] Cursor Token: {token}")

    browser.quit(force=True, del_data=True)

    return {
        'username': email,
        'password': password,
        'token': token
    }

def register_cursor(number, max_workers):

    options = ChromiumOptions()
    options.auto_port()
    # Use turnstilePatch from https://github.com/TheFalloutOf76/CDP-bug-MouseEvent-.screenX-.screenY-patcher
    options.add_extension("turnstilePatch")

    # Run the code using multithreading
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sign_up, copy.deepcopy(options)) for _ in range(number)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

    results = [result for result in results if result["token"] is not None]
    if len(results) > 0:
        formatted_date = datetime.now().strftime("%Y-%m-%d")

        csv_file = f"./output_{formatted_date}.csv"
        token_file = f"./token_{formatted_date}.csv"

        fieldnames = results[0].keys()

        # Write username, password, token into a csv file
        with open(csv_file, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not os.path.isfile(csv_file):
                writer.writeheader()
            writer.writerows(results)

        # Only write token to csv file, without header
        tokens = [{"token": row["token"]} for row in results]
        with open(token_file, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["token"])
            writer.writerows(tokens)

    return results


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Cursor Registor")
    parser.add_argument("--number", type=int, default=2, help="How many account you want")
    parser.add_argument("--max_workers", type=int, default=1, help="How many workers in multithreading")

    # The parameters with name starts with oneapi are used to uploead the cookie token to one-api, new-api, chat-api server.
    parser.add_argument("--oneapi", action="store_true", help="Enable One-API or not")
    parser.add_argument("--oneapi_url", type=str, required=False, help="URL link for One-API website")
    parser.add_argument("--oneapi_token", type=str, required=False, help="Token for One-API website")
    parser.add_argument(
        "--oneapi_channel_url",
        type=str,
        required=False,
        help="Base url for One-API channel",
    )

    args = parser.parse_args()
    number = args.number
    max_workers = args.max_workers
    use_oneapi = args.oneapi
    oneapi_url = args.oneapi_url
    oneapi_token = args.oneapi_token
    oneapi_channel_url = args.oneapi_channel_url

    account_infos = register_cursor(number, max_workers)
    tokens = list(set([row['token'] for row in account_infos]))
    print(f"[Register] Register {len(tokens)} Accounts Successfully")
    
    if use_oneapi and len(account_infos)>0:
        from tokenManager.oneapi_manager import OneAPIManager

        oneapi = OneAPIManager(oneapi_url, oneapi_token)
        response = oneapi.add_channel("Cursor",
                                      oneapi_channel_url,
                                      tokens,
                                      OneAPIManager.cursor_models)
        print(f'[OneAPI] Add Channel Request Status Code: {response.status_code}')
        print(f'[OneAPI] Add Channel Request Response Body: {response.json()}')
