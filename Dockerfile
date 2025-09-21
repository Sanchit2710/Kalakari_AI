# Use an official Python 3.9 image as the base
FROM python:3.9-slim

# Set the working directory inside the server
WORKDIR /app

# Copy the requirements file into the server
COPY requirements.txt .

# Install all the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the server
COPY . .

# The command that starts your web server
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app"]