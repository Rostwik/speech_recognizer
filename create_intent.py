import json

from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=list([message_texts]))
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )


def main():
    project_id = 'dvmn-speech-recognizer'

    with open("files/intents.json", "r", encoding="UTF-8") as file:
        file_contents = file.read()
        intents = json.loads(file_contents)

        intents_name = 'Устройство на работу'

    create_intent(
        project_id,
        display_name=intents_name,
        training_phrases_parts=intents[intents_name]['questions'],
        message_texts=intents[intents_name]['answer']
    )


if __name__ == '__main__':
    main()
