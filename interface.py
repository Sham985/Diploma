import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine
from config import community_token, acces_token
from core import VkTools
from data_base import DBTools


class BotInterface():
    def __init__(self, community_token, acces_token, engine):
        self.vk = vk_api.VkApi(token = community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.bd_tools = DBTools(engine)
        self.check_user = DBTools(engine)

    def message_send(self, user_id, message, attachment = None):
        self.vk.method('messages.send',
                {'user_id': user_id,
                'message': message,
                'attachment': attachment,
                'random_id': get_random_id(),
                })
    
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}')

                elif event.text.lower() == 'поиск':
                    self.message_send(event.user_id, 'Начинаем поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        self.offset += 10

                    while self.bd_tools.check_user(event.user_id, worksheet["id"]) is True:
                        worksheet = self.worksheets.pop() 

                    if self.bd_tools.check_user(event.user_id, worksheet["id"]) is False:
                        self.bd_tools.add_user(event.user_id, worksheet["id"])

                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                        self.message_send(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}', attachment = photo_string)

                

                elif event.text.lower() == 'пока':
                    self.message_send(event.user_id, 'До новых встреч')
                else:
                    self.message_send(event.user_id, 'Уточните запрос')



if __name__ == '__main__':
    bot_interface = BotInterface(community_token, acces_token, engine = create_engine())
    bot_interface.event_handler()

