import time
import json
import telebot
import openai

# Токены
bot = telebot.TeleBot("", parse_mode=None)
openai.api_key = ""


def call_openai_api(*args, **kwargs):
    return openai.ChatCompletion.create(*args, **kwargs)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f'~~Здравствуй! Я Chat GPT bot~~\n\n'
                                      f'° - Просто задай мне вопрос\n'
                                      f'~~~~~~~~~~~~~~~~')


# Получение полного запроса на основе предыдущих
def get_prompt(data):
    prompt = ""
    for i in data:
        prompt += i["question"] + "\n" + i["answer"] + "\n"
    return prompt


@bot.message_handler(content_types=['text'])
def quest(message):
    bot.send_message(message.chat.id, "Запрос обрабатывается...")
    # Открытие json файла
    with open('data.json', 'rb') as file:
        json_bytes = file.read()
    json_str = json_bytes.decode('utf-8')
    data = json.loads(json_str)
    if str(message.chat.id) in data["users"]:
        prompt = get_prompt(data["users"][str(message.chat.id)])
        prompt += message.text
    else:
        prompt = message.text
    completion = call_openai_api(model="gpt-3.5-turbo", messages=[
        {"role": "user", "content": prompt}
    ])

    # Заполнение json файла
    if str(message.chat.id) in data["users"]:
        data["users"][str(message.chat.id)].append({"question": str(message.text),
                                                    "answer": completion.choices[0].message.content})
    else:
        data["users"][str(message.chat.id)] = [{"question": str(message.text),
                                                "answer": completion.choices[0].message.content}]
    with open("data.json", "w", encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    bot.send_message(message.chat.id, completion.choices[0].message.content)


def infinity_polling(self, *args, **kwargs):
    while not self.__stop_polling.is_set():
        try:
            self.polling(*args, **kwargs)
        except Exception as e:
            time.sleep(5)
            pass
    telebot.logger.info("Break infinity polling")


if __name__ == '__main__':
    bot.infinity_polling(none_stop=True, interval=0)
