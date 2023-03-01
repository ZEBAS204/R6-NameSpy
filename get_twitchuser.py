import traceback
import requests


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
        print(f'Something went wrong while parsing channel from "{userName}"')
        traceback.print_exc()
        return False
