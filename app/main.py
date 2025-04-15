from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
from config import TOKEN

vk_session = VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def echo(id, text):
    vk.messages.send(user_id=id, message=text, random_id=0)

def main_loop(longpoll: VkLongPoll):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg = event.text.lower()
                id = event.user_id
                echo(id, msg)


if __name__ == "__main__":
    main_loop(longpoll)