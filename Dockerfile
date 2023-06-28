# Use the official Python base image
FROM python:3.9

ARG GMSH_VERSION="4_11_1"


# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    ninja-build \
    git \
    libgl1-mesa-dev \
    libocct-foundation-dev \
    libocct-data-exchange-dev

# Install GMSH
RUN git clone -b gmsh_${GMSH_VERSION} --single-branch --depth 1 https://gitlab.onelab.info/gmsh/gmsh.git && \
    cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DENABLE_BUILD_DYNAMIC=1  -DENABLE_OPENMP=1 -B build-dir -S gmsh && \
    cmake --build build-dir && \
    cmake --install build-dir && \
    rm -rf /tmp/*

# GMSH installs python library in /usr/local/lib, see: https://gitlab.onelab.info/gmsh/gmsh/-/issues/1414
ENV PYTHONPATH=/usr/local/lib:$PYTHONPATH


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirementsWebApp.txt .
RUN pip install -r requirementsWebApp.txt

# Install the Python dependencies
#RUN pip install -r requirementsWebApp.txt
# Copy the application code to the container
COPY . .

# Expose the port on which the Flask application runs
EXPOSE 5002

# Run the Flask application
CMD ["python", "app.py"]
