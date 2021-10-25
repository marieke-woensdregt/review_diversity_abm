FROM python:3

ADD /src /src

RUN pip install -r /src/requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes
ENV PYTHONUNBUFFERED Yes

WORKDIR /src

CMD python main.py