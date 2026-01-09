import azure.cognitiveservices.speech as speechsdk
import time
import os
import json
from datetime import timedelta

# Configuration - A configurer via variables d'environnement
speech_key = os.getenv('SPEECH_KEY')
service_region = os.getenv('SERVICE_REGION', 'canadaeast')
audio_file = os.getenv('AUDIO_FILE', 'audio.wav')
base_output = os.getenv('OUTPUT_BASE', 'transcription')

if not speech_key:
    print("❌ Erreur: SPEECH_KEY non defini")
    print("   Definissez la variable d'environnement SPEECH_KEY")
    exit(1)

print("Démarrage de la transcription...")
print(f"Fichier audio: {audio_file}")
print(f"Langue: français (fr-FR)")

# Configuration du service Speech
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "fr-FR"
speech_config.request_word_level_timestamps()
speech_config.output_format = speechsdk.OutputFormat.Detailed

# Configuration de la source audio
audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

# Créer le recognizer
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Variables pour stocker les résultats détaillés
all_results = []
detailed_results = []
done = False
segment_index = 0

def format_timestamp(milliseconds):
    """Convertir millisecondes en format timestamp SRT/VTT"""
    td = timedelta(milliseconds=milliseconds / 10000)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = int(td.total_seconds() % 60)
    ms = int((td.total_seconds() % 1) * 1000)
    return hours, minutes, seconds, ms

def stop_cb(evt):
    """Callback pour arrêter la reconnaissance"""
    global done
    print('\nTranscription terminée.')
    done = True

def recognized_cb(evt):
    """Callback pour chaque segment reconnu avec détails"""
    global segment_index
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('.', end='', flush=True)
        segment_index += 1
        
        # Stocker le texte simple
        all_results.append(evt.result.text)
        
        # Stocker les détails complets
        result_json = json.loads(evt.result.json)
        
        segment_data = {
            'index': segment_index,
            'text': evt.result.text,
            'offset': evt.result.offset,
            'duration': evt.result.duration,
            'confidence': result_json.get('NBest', [{}])[0].get('Confidence', 0) if 'NBest' in result_json else 0,
            'words': []
        }
        
        # Extraire les mots avec timestamps si disponibles
        if 'NBest' in result_json and len(result_json['NBest']) > 0:
            nbest = result_json['NBest'][0]
            if 'Words' in nbest:
                for word in nbest['Words']:
                    segment_data['words'].append({
                        'word': word.get('Word', ''),
                        'offset': word.get('Offset', 0),
                        'duration': word.get('Duration', 0),
                        'confidence': word.get('Confidence', 0)
                    })
        
        detailed_results.append(segment_data)
        
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print('x', end='', flush=True)

def canceled_cb(evt):
    """Callback en cas d'erreur"""
    if evt.result.reason != speechsdk.ResultReason.EndOfStream:
        print(f'\nErreur: {evt.result.cancellation_details.reason}')
        if evt.result.cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f'Détails: {evt.result.cancellation_details.error_details}')

# Connecter les callbacks
speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(canceled_cb)

# Démarrer la reconnaissance continue
speech_recognizer.start_continuous_recognition()

# Attendre la fin
while not done:
    time.sleep(0.5)

# Arrêter la reconnaissance
speech_recognizer.stop_continuous_recognition()

print(f"\n\nGénération des fichiers de sortie...")

# 1. Format TXT - Texte simple
txt_file = f"{base_output}.txt"
with open(txt_file, 'w', encoding='utf-8') as f:
    for text in all_results:
        f.write(text + '\n')
print(f"✓ TXT: {txt_file}")

# 2. Format JSON simple
json_simple_file = f"{base_output}-simple.json"
with open(json_simple_file, 'w', encoding='utf-8') as f:
    json.dump({
        'text': ' '.join(all_results),
        'segments': len(all_results),
        'total_chars': sum(len(text) for text in all_results)
    }, f, ensure_ascii=False, indent=2)
print(f"✓ JSON simple: {json_simple_file}")

# 3. Format JSON détaillé
json_detailed_file = f"{base_output}-detailed.json"
with open(json_detailed_file, 'w', encoding='utf-8') as f:
    json.dump({
        'language': 'fr-FR',
        'segments': detailed_results,
        'total_segments': len(detailed_results),
        'full_text': ' '.join(all_results)
    }, f, ensure_ascii=False, indent=2)
print(f"✓ JSON détaillé: {json_detailed_file}")

# 4. Format SRT (sous-titres)
srt_file = f"{base_output}.srt"
with open(srt_file, 'w', encoding='utf-8') as f:
    for segment in detailed_results:
        start_h, start_m, start_s, start_ms = format_timestamp(segment['offset'])
        end_offset = segment['offset'] + segment['duration']
        end_h, end_m, end_s, end_ms = format_timestamp(end_offset)
        
        f.write(f"{segment['index']}\n")
        f.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n")
        f.write(f"{segment['text']}\n\n")
print(f"✓ SRT: {srt_file}")

# 5. Format WebVTT
vtt_file = f"{base_output}.vtt"
with open(vtt_file, 'w', encoding='utf-8') as f:
    f.write("WEBVTT\n\n")
    for segment in detailed_results:
        start_h, start_m, start_s, start_ms = format_timestamp(segment['offset'])
        end_offset = segment['offset'] + segment['duration']
        end_h, end_m, end_s, end_ms = format_timestamp(end_offset)
        
        f.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:03d}\n")
        f.write(f"{segment['text']}\n\n")
print(f"✓ VTT: {vtt_file}")

# 6. Format avec mots détaillés
words_file = f"{base_output}-words.json"
words_data = []
for segment in detailed_results:
    for word in segment['words']:
        words_data.append({
            'word': word['word'],
            'start_time': word['offset'] / 10000000,  # Convertir en secondes
            'duration': word['duration'] / 10000000,
            'confidence': word['confidence']
        })

with open(words_file, 'w', encoding='utf-8') as f:
    json.dump({
        'words': words_data,
        'total_words': len(words_data)
    }, f, ensure_ascii=False, indent=2)
print(f"✓ Mots détaillés: {words_file}")

print(f"\n{'='*60}")
print(f"Transcription complétée!")
print(f"Segments transcrits: {len(all_results)}")
print(f"Longueur totale: {sum(len(text) for text in all_results)} caractères")
print(f"Mots transcrits: {len(words_data)}")
print(f"{'='*60}")
