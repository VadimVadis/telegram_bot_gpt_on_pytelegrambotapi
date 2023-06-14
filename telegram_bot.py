import time
import json
import telebot
import openai

bot = telebot.TeleBot("5941193514:AAHaI47TlkBSYAjoDsontrkEmgM493vJyTA", parse_mode=None)
openai.api_key = "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"


def call_openai_api(*args, **kwargs):
    return openai.ChatCompletion.create(*args, **kwargs)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f'~~Здравствуй! Я Chat GPT bot~~\n\n'
                                      f'° - "/quest + запрос" - Задать вопрос,\n'
                                      f'~~~~~~~~~~~~~~~~')


@bot.message_handler(commands=['quest'], func=lambda message: True)
def quest(message):
    bot.send_message(message.chat.id, "Запрос обрабатывается...")
    print(message.text)
    completion = call_openai_api(model="gpt-3.5-turbo", messages=[
        {"role": "user", "content": message.text[7:]}
    ])
    print(message.text[7:])
    with open('data.json') as f:
        data = json.load(f)
    if str(message.chat.id) in data["users"]:
        data["users"][message.chat.id].append({"question": str(message.text[7:]),
                                               "answer": completion.choices[0].message.content})
    else:
        data["users"][message.chat.id] = [{"question": str(message.text[7:]),
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
