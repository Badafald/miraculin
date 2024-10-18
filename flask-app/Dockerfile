FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the app code into the container
COPY . /app

# Copy templates and static directories explicitly if needed
COPY /templates /app/templates
COPY /static /app/static

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
