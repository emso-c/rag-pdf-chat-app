# Alpine distro does not support Chromadb installation as it uses the
# musl C standard lib. Chromadb dependency 'onnxruntime' is built using libgc.
# Reference: https://stackoverflow.com/a/78566401
# FROM python:3.12-alpine
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.test.txt .

# Need to install the following packages to be able to
# handle I/O operations with shared object files.
# Reference: https://stackoverflow.com/a/62786543
RUN apt-get update && apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 -y

RUN pip install --no-cache-dir -r requirements.test.txt

ENV ENV='dev'

COPY . .

CMD ["pytest", "-v"]
