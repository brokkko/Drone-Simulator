FROM ubuntu:20.04

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY /sim /usr/src/app

RUN apt-get update -y
RUN apt-get install -y net-tools
RUN apt install -y iproute2
RUN apt-get install -y libxml2
RUN apt-get install -y libx11-dev
RUN apt-get install -y libpng16-16
RUN apt install -y libxext6
RUN apt-get install -y libxfixes-dev
RUN apt-get install -y libxft2
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN pip install serial


RUN chmod +x Autopilot
RUN chmod +x simulator
RUN chmod +x start.sh

EXPOSE 8000

CMD "./start.sh"