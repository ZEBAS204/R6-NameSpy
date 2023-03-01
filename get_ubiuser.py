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

MAIL = environ.get("USER_MAIL") or None
PASSWORD = environ.get("USER_PASSWORD") or None

HEADERS = {
    "Ubi-AppId": "2c2d31af-4ee4-4049-85dc-00dc74aef88f",
    "Ubi-RequestedPlatformType": "uplay",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/97.0",
}


def getAuthToken():
    global AUTH_TOKEN

    print("getAuthToken(): getting auth token")

    if AUTH_TOKEN:
        return AUTH_TOKEN

    if not MAIL or not PASSWORD:
        raise Exception("\nCan not authenticate user without MAIL and/or PASSWORD!\n")

    try:
        response = requests.post(
            "https://public-ubiservices.ubi.com/v3/profiles/sessions",
            auth=HTTPBasicAuth(MAIL, PASSWORD),
            headers={**HEADERS, "Content-Type": "application/json"},
        )

        if not response.status_code == 200:
            raise Exception("Request error", response, response.content)

        """
        Authentication response should look like:
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
        print(f"Something went wrong while trying to get authentication token!")
        traceback.print_exc()
        return ""


def getHeaders():
    global AUTH_TOKEN

    if not AUTH_TOKEN:
        getAuthToken()

    return {
        **HEADERS,
        "Ubi-SessionId": AUTH_TOKEN["sessionId"] or "",
        "Authorization": f"Ubi_v1 t={AUTH_TOKEN['ticket']}",
    }


def getUbiUser(userName):
    print(f"getUbiUser(): userName={userName}")

    try:
        url = f"https://public-ubiservices.ubi.com/v3/profiles?nameOnPlatform={userName}&platformType=uplay"
        response = requests.get(url, headers=getHeaders())

        if not response.status_code == 200:
            raise Exception("Request error", response, response.content)

        """
        Response:
        {
            'profiles': [{
                'profileId': string,
                'userId': string
                'platformType': 'uplay',
                'idOnPlatform': string
                'nameOnPlatform': string
                }
            ]}
        }
        """

        # print(response.content)
        user = response.json()
        return user["profiles"][0]

    except Exception:
        print(f'Something went wrong while parsing account from "{userName}"')
        traceback.print_exc()


def getUserApplications(userID):
    print(f"getUserApplications(): userID={userID}")

    try:
        url = f" https://public-ubiservices.ubi.com/v1/profiles/{userID}/gamesplayed"
        response = requests.get(url, headers=getHeaders())

        if not response.status_code == 200:
            raise Exception("Request error", response, response.content)

        print(response.content)

        return response.json()

    except Exception:
        print(f'Something went wrong while parsing user applications "{userID}"')
        traceback.print_exc()
