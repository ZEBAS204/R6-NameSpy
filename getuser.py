from os import environ
from dotenv import load_dotenv
import traceback
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

"""
* ----------------------------------------------------------------
* Original code I adapted to use with Python:
* https://github.com/Digneety/Argali/blob/master/Program.cs
*
* You can also see r6api.js:
* https://github.com/danielwerg/r6api.js
* ----------------------------------------------------------------
"""

AUTH_TOKEN = None

MAIL = environ.get('USER_MAIL') or None
PASSWORD = environ.get('USER_PASSWORD') or None

HEADERS = {
    "Ubi-AppId": "2c2d31af-4ee4-4049-85dc-00dc74aef88f",
    "Ubi-RequestedPlatformType": "uplay",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/97.0"
}


class User():

    def __init__(self, mail=None, password=None):
        global MAIL, PASSWORD, AUTH_TOKEN

        self.mail = mail or MAIL
        self.password = password or PASSWORD
        self.token = AUTH_TOKEN or self.getAuthToken()

    def getHeaders(self):
        global HEADERS

        if not AUTH_TOKEN:
            self.getAuthToken()

        return {
            **HEADERS,
            "Ubi-SessionId": AUTH_TOKEN['sessionId'] or "",
            "Authorization": f"Ubi_v1 t={AUTH_TOKEN['ticket']}"
        }

    def getAuthToken(self):
        print('getAuthToken(): getting auth token')

        if self.AUTH_TOKEN:
            return AUTH_TOKEN

        if not MAIL or not PASSWORD:
            raise Exception(
                "\nCan not authenticate user without MAIL and/or PASSWORD!\n")

        try:
            response = requests.post(
                'https://public-ubiservices.ubi.com/v3/profiles/sessions',
                auth=HTTPBasicAuth(MAIL, PASSWORD),
                headers={
                    **HEADERS,
                    'Content-Type': 'application/json'
                })

            if not response.status_code == 200:
                raise Exception("Request error", response, response.content)

            """
            Authentication response shoud look like:
            {
                platformType: "uplay"
                ! ticket: string
                twoFactorAuthenticationTicket: boolean?
                profileId: string
                userId: string
                nameOnPlatform: string
                environment: "Prod"
                expiration: Date
                spaceId: string
                clientIp: string
                clientIpCountry: string{2,}
                serverTime: Date
                sessionId: string
                sessionKey: string
                rememberMeTicket: boolean
            }
            """
            # print(response.content)

            # * Save response to the static variable
            AUTH_TOKEN = response.json()

        except Exception:
            print(f'Something went wrong while trying to get authentication token!')
            traceback.print_exc()
            return ""

    def isStreaming(userName):
        try:
            response = requests.get(f'https://www.twitch.tv/{userName}')
            # print(response.content)

            # * We need to check if the response contains "isLiveBroadcast" text
            # * and if so then it means the user is live
            if 'isLiveBroadcast' in response.content.decode('utf-8'):
                print(f'User "{userName}" is streaming')
                return True

            print(f'User "{userName}" is offline')
            return False

        except Exception:
            print(
                f'Something went wrong while parsing channel from "{userName}"')
            traceback.print_exc()
            return False
