FROM python:3

ADD /src

RUN pip install -r /src/requirements.txt

RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

ENV MY_PARAMETER=""

CMD python /src/main.py --my-parameter $MY_PARAMETER