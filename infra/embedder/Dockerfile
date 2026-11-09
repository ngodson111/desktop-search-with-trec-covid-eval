FROM ollama/ollama:0.5.7

ENV EMBED_MODEL=all-minilm

RUN ollama serve & sleep 5 && ollama pull $EMBED_MODEL
