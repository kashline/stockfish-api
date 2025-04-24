
FROM python:3.13-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    g++ make curl unzip git && \
    rm -rf /var/lib/apt/lists/*

# Build Stockfish from source
WORKDIR /opt
RUN git clone https://github.com/official-stockfish/Stockfish.git && \
    cd Stockfish/src && \
    make build

# Add your Flask app
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Use unbuffered output
ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD ["python", "app.py"]
