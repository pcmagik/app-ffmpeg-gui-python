FROM python:3.9-alpine

# Install ffmpeg
RUN apk add --no-cache ffmpeg

# Set working directory
WORKDIR /app

# Create required directories
RUN mkdir -p /app/uploads /app/temp/GIFY /app/gifs

# Copy current directory contents to /app
COPY . /app

# Install Python dependencies
RUN pip install flask

# Expose port
EXPOSE 8080

# Run app.py when the container launches
CMD ["python", "app.py"]
