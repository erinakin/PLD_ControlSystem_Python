# Contains instructions to build Docker image for the Python Control System
FROM continuumio/miniconda3

# Create a new envirnment with Python 3.11
RUN conda create -n py311 python=3.11 -y

# Activate the environment and install necessary packages
SHELL ["conda", "run", "-n", "py311", "/bin/bash", "-c"]

# Set the working directory
WORKDIR /usr/src/app

EXPOSE 5006

# Install Jupyter Notebook or any other dependencies
RUN conda install -n py311 notebook -y

# Copy requirements.txt into the container at /usr/src/app
COPY ./docs/requirements.txt /usr/src/app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# Copy the src directory into the container at /usr/src/app
COPY src/ /usr/src/app

CMD ["panel", "serve", "src/app.py", "--port", "5006", "--allow-websocket-origin", "*"]