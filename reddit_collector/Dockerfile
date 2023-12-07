FROM python:3.9 

WORKDIR /my_app


COPY . /my_app/

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "get_reddits.py"]
