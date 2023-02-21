FROM python:3.8
RUN mkdir -p /app
WORKDIR /app 

COPY requirements.txt /
RUN pip install --requirement /requirements.txt

COPY ./app /app

RUN apt-get update && \
    apt-get -y install libgl1-mesa-glx

EXPOSE 6002
CMD ["uvicorn", "main:app", "--host=0.0.0.0" , "--reload" , "--port", "6002"]