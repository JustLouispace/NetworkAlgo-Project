# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run main.py when the container launches
CMD ["python", "main.py"]
