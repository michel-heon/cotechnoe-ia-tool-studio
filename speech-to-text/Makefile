# Makefile pour la transcription de fichiers mp4 en texte
# Usage: make transcribe INPUT=chemin/vers/fichier.mp4

# Charger les variables depuis le fichier .env
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variables de configuration Azure Speech
SPEECH_KEY ?=
SERVICE_REGION ?= canadaeast
LANGUAGE ?= fr-FR

# Fichiers
INPUT ?= input.mp4
AUDIO_WAV = $(basename $(notdir $(INPUT)))-audio.wav
OUTPUT_BASE = $(basename $(notdir $(INPUT)))-transcription
OUTPUT_TXT = $(OUTPUT_BASE).txt

# Commandes
FFMPEG = ffmpeg
PYTHON = python3
SCRIPT_DIR = scripts

.PHONY: all transcribe convert clean help

all: help

transcribe: $(OUTPUT_TXT)
	@echo "Transcription terminee: $(OUTPUT_BASE).*"

convert: $(AUDIO_WAV)
	@echo "Conversion audio terminee: $(AUDIO_WAV)"

$(AUDIO_WAV): $(INPUT)
	@echo "Extraction de l'audio depuis $(INPUT)..."
	$(FFMPEG) -i "$(INPUT)" -ar 16000 -ac 1 -c:a pcm_s16le "$(AUDIO_WAV)" -y

$(OUTPUT_TXT): $(AUDIO_WAV)
	@if [ -z "$(SPEECH_KEY)" ]; then \
		echo "Erreur: SPEECH_KEY non defini"; \
		exit 1; \
	fi
	@echo "Transcription de $(AUDIO_WAV) en $(LANGUAGE)..."
	@SPEECH_KEY="$(SPEECH_KEY)" SERVICE_REGION="$(SERVICE_REGION)" LANGUAGE="$(LANGUAGE)" AUDIO_FILE="$(AUDIO_WAV)" OUTPUT_BASE="$(OUTPUT_BASE)" $(PYTHON) $(SCRIPT_DIR)/transcribe.py

clean:
	@echo "Nettoyage des fichiers generes..."
	@rm -f *-audio.wav *-transcription.* transcribe_temp.py
	@echo "Nettoyage termine"

help:
	@echo "Makefile pour la transcription mp4 en texte"
	@echo ""
	@echo "Usage:"
	@echo "  make transcribe INPUT=fichier.mp4"
	@echo "  make convert INPUT=fichier.mp4"
	@echo "  make clean"
