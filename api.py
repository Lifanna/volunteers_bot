import requests
import dotenv, os

dotenv.load_dotenv()

class APIHandler:
    def __init__(self):
        self.MAIN_URL = os.getenv('MAIN_URL')

    def get_user_profile(self, telegram_user_id):
        url = self.MAIN_URL + "/api/user-profile/" + telegram_user_id + "/"

        response = requests.get(url)

        user_profile = {}

        if response.status_code == 200:
            data = response.json()
            user_profile = response.json()
            print("Информация о пользователе:")
            print("Имя:", data.get('first_name'))
            print("Фамилия:", data.get('last_name'))
            print("Направление:", data.get('direction'))
            print("Количество ссылок за все время:", data.get('total_links'))
            print("Подтвержденные за все время:", data.get('total_approved'))
            print("Подтвержденные за текущий месяц:", data.get('total_approved_current_month'))
        else:
            print("Ошибка при запросе:", response.status_code)

        return user_profile

    def send_link(self, telegram_user_id, link):
        url = self.MAIN_URL + "/api/send_link/"

        response = requests.post(url, data={
            "telegram_user_id": telegram_user_id,
            "link": link,
        })

        successful = False

        if response.status_code == 201:
            successful = True

        return successful

    def login(self, telegram_user_id, phone_number):
        url = self.MAIN_URL + "/api/auth/signin/"

        response = requests.post(url, data={
            "phone_number": phone_number,
            "telegram_user_id": telegram_user_id,
        })

        successful = False

        if response.status_code == 200:
            successful = True

        return successful
