import maritalk
import telebot
from dotenv import load_dotenv
import os


prompt = """Você é um Chatbot de Trivia Quiz, que é um jogo de \
perguntas e respostas rápidas de conhecimento geral. \
Faça perguntas e corrija resposta de acordo.

Pergunta: Qual é a capital do Brasil?
Resposta: Brasília`
Correção: Correto!

Pergunta: Qual é o maior osso do corpo humano?
Resposta: Fêmur
Correção: Correto!

Pergunta: Qual é o maior planeta do sistema solar?
Resposta: Saturno
Correção: Errado! O maior planeta do sistema solar é Júpiter.

Pergunta: Qual é o menor país do mundo?
Resposta: Japão
Correção: Errado! O menor país do mundo é Vaticano.

Pergunta: """


class Chat:
    def __init__(self, chat_id: int):
        global prompt

        self.chat_id = chat_id
        self.prompt = prompt
        self.esperando_resposta = False


chats: list[Chat] = []

esperando_resposta = False

if __name__ == "__main__":
    load_dotenv()

    CHAVE_MARITACA = os.getenv("CHAVE_MARITACA")
    CHAVE_TELEGRAM = os.getenv("CHAVE_TELEGRAM")

    model = maritalk.MariTalk(
        key=CHAVE_MARITACA,
        model="sabia-3"
    )

    bot = telebot.TeleBot(CHAVE_TELEGRAM)

    def get_chat(chat_id: int) -> Chat or None:
        for chat in chats:
            if chat.chat_id == chat_id:
                return chat
        return None

    @bot.message_handler(commands=["start"])
    def bem_vindo(message):
        novo_chat = Chat(message.chat.id)
        chats.append(novo_chat)
        bot.reply_to(
            message, "Ola! Eu sou uma Bot de Trivia Quiz, peça uma pergunta com /pergunta e insira a resposta!")

    @bot.message_handler(commands=["pergunta"])
    def pergunta(message):
        chat = get_chat(message.chat.id)

        if chat is None:
            bot.reply_to(
                message, "Você não iniciou o chat comigo. Digite /start para começar.")
            return

        if chat.esperando_resposta:
            return

        pergunta = model.generate(
            chat.prompt,
            chat_mode=False,
            do_sample=False,
            stopping_tokens=["\n"]
        )["answer"]

        chat.prompt += pergunta + "\nResposta: "

        bot.reply_to(message, pergunta)

        chat.esperando_resposta = True

    @bot.message_handler(func=lambda message: True)
    def resposta(message):
        chat = get_chat(message.chat.id)

        if chat is None:
            bot.reply_to(
                message, "Você não iniciou o chat comigo. Digite /start para começar.")
            return

        if not chat.esperando_resposta:
            return

        resposta = message.text
        chat.prompt += resposta + "\nCorreção: "

        correcao = model.generate(
            chat.prompt,
            chat_mode=False,
            do_sample=False,
            stopping_tokens=["\n"]
        )["answer"]

        chat.prompt += correcao + "\n\nPergunta: "
        bot.reply_to(message, correcao)

        chat.esperando_resposta = False

    bot.infinity_polling()
