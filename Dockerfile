FROM ubuntu:latest

WORKDIR /app

COPY . /app

WORKDIR /app/Multiple_Classifier_Pipeline

RUN apt-get update && apt-get install -y \
    libxrender1 \
    #xvfb \
    #libglu1-mesa \
    #freeglut3-dev \
    python3 \
    python3-pip 

RUN pip3 install --no-cache-dir -r requirements1.txt

CMD [ "python3", "Pipeline.py" ]



