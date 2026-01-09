#!/usr/bin/env python3
"""Script de transcription simple pour Azure Speech"""

import azure.cognitiveservices.speech as speechsdk
import time
import os
import sys

# Récupérer les paramètres depuis les variables d'environnement
speech_key = os.getenv('SPEECH_KEY')
service_region = os.getenv('SERVICE_REGION', 'canadaeast')
language = os.getenv('LANGUAGE', 'fr-FR')
audio_file = os.getenv('AUDIO_FILE')
output_base = os.getenv('OUTPUT_BASE', 'transcription')

if not speech_key:
    print('❌ Erreur: SPEECH_KEY non défini')
    sys.exit(1)

if not audio_file:
    print('❌ Erreur: AUDIO_FILE non défini')
    sys.exit(1)

print(f'Transcription de {audio_file} en {language}...')

# Configuration du service Speech
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = language
audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Variables pour stocker les résultats
all_results = []
done = False

def stop_cb(evt):
    global done
    done = True

def recognized_cb(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('.', end='', flush=True)
        all_results.append(evt.result.text)

# Connecter les callbacks
speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

# Démarrer la reconnaissance continue
speech_recognizer.start_continuous_recognition()

# Attendre la fin
while not done:
    time.sleep(0.5)

# Arrêter la reconnaissance
speech_recognizer.stop_continuous_recognition()

# Sauvegarder les résultats
output_file = f"{output_base}.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    for text in all_results:
        f.write(text + ' ')

print(f'\n✓ {len(all_results)} segments, {sum(len(t) for t in all_results)} caractères')
