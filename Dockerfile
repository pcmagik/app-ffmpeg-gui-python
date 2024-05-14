FROM python:3.9-alpine
RUN apk add --no-cache ffmpeg
WORKDIR /app
COPY . /app
RUN pip install flask
EXPOSE 8080
CMD ["python", "server.py"]
