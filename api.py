import requests
import dotenv, os

dotenv.load_dotenv()

class APIHandler:
    def __init__(self):
        self.MAIN_URL = "http://91.107.127.133"
        # self.MAIN_URL = "http://localhost:8000"

        print("DDDD:", self.MAIN_URL)

    def get_user_links(self, telegram_user_id):
        url = self.MAIN_URL + "/api/links/" + str(telegram_user_id)

        response = requests.get(url)

        user_links = {}

        if response.status_code == 200:
            user_links = response.json()
        else:
            print("Ошибка при запросе:", response.status_code)

        return user_links

    def get_rating(self):
        url = self.MAIN_URL + "/api/rating/"

        response = requests.get(url)

        user_scores = {}

        if response.status_code == 200:
            user_scores = response.json()
        else:
            print("Ошибка при запросе:", response.status_code)

        return user_scores

    def get_tasks(self, telegram_user_id):
        url = self.MAIN_URL + "/api/tasks/" + str(telegram_user_id)

        response = requests.get(url)

        user_links = {}

        if response.status_code == 200:
            user_links = response.json()
        else:
            print("Ошибка при запросе:", response.status_code)

        return user_links

    def get_user_profile(self, telegram_user_id):
        url = self.MAIN_URL + "/api/user-profile/" + str(telegram_user_id)

        response = requests.get(url)

        user_profile = {}

        if response.status_code == 200:
            user_profile = response.json()
        else:
            print("Ошибка при запросе:", response.status_code)

        response = "Имя: " + str(user_profile.get('first_name')) + "\n" \
        "Фамилия: " + str(user_profile.get('last_name')) + "\n" \
        "Направление: " + str(user_profile.get('direction')) + "\n" \
        "Количество ссылок за все время: " + str(user_profile.get('total_links')) + "\n" \
        "Подтвержденные за все время: " + str(user_profile.get('total_approved')) + "\n" \
        "Подтвержденные за текущий месяц: " + str(user_profile.get('total_approved_current_month')) + "\n"

        return response

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

    def verify(self, telegram_user_id, phone_number):
        url = self.MAIN_URL + "/api/auth/verify/"

        response = requests.post(url, data={
            "phone_number": phone_number,
            "telegram_user_id": telegram_user_id,
        })

        successful = False

        if response.status_code == 200:
            successful = True

        return successful

    def signin(self, telegram_user_id):
        url = self.MAIN_URL + "/api/auth/signin/"

        response = requests.post(url, data={
            "telegram_user_id": telegram_user_id,
        })

        successful = False

        if response.status_code == 200:
            successful = True

        return successful

    def send_task(self, task_json):
        url = self.MAIN_URL + "/api/tasks/new/"

        response = requests.post(url, data=task_json)

        successful = False

        print(response.status_code)

        if response.status_code == 201:
            successful = True

        return successful
