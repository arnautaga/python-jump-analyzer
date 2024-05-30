import SpeechRecognition as sr
import pyttsx3

class TrainingAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.speaker = pyttsx3.init()

    def listen(self):
        with sr.Microphone() as source:
            self.speaker.say("Por favor, habla para decirme qué tipo de entrenamiento necesitas.")
            self.speaker.runAndWait()
            print("Escuchando...")
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio, language="es-ES")
            return text.lower()
        except sr.UnknownValueError:
            return "No pude entender lo que dijiste."
        except sr.RequestError:
            return "Lo siento, hubo un error en la solicitud de reconocimiento de voz."

    def respond(self, text):
        print("Asistente: ", text)
        self.speaker.say(text)
        self.speaker.runAndWait()

if __name__ == "__main__":
    assistant = TrainingAssistant()
    while True:
        command = assistant.listen()
        print("Usuario: ", command)
        assistant.respond("Entendido, estás trabajando en: " + command)
