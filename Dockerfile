FROM python:3

ADD /src /src
ADD requirements.txt requirements.txt

RUN pip install -r /src/requirements.txt

RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

ENV MY_PARAMETER=""

WORKDIR /src

CMD python main.py --my-parameter $MY_PARAMETER