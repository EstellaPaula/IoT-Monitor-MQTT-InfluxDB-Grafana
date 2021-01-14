FROM python:3.8

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN apt-get update && apt-get install -y netcat
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy source code
COPY . /usr/src/app/

CMD ["python", "-u", "main.py"]