def catcherrors(e, chat):
    if e.result.status_code == 400:
        if 'chat not found' in e.description:
            print("Bad Request: chat not found", chat)
        elif 'not enough rights' in e.description:
            print("Bad Request: not enough rights to send text messages to the chat", chat)
        else:
            raise e
    elif e.result.status_code == 403:
        if 'bot was blocked by the user' in e.description:
            print("Forbidden: bot was blocked by the chat", chat)
        elif 'bot was kicked from the group chat' in e.description:
            print("Forbidden: bot was kicked from the chat", chat)
        elif 'user is deactivated' in e.description:
            print('user is deactivated', chat)
        else:
            raise e
    else:
        raise e

