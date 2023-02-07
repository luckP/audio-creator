# Dockerfile, Image, Container
FROM python:3.9

ADD main.py .

RUN pip install sys os eyed3

CMD ["python", "main.py"]
