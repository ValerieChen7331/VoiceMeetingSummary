FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

# Maintainer info
LABEL maintainer="StevenHu <n000192533@npc.com.tw>"

# Set the working directory in the container
RUN  mkdir -p  /GAI_web
WORKDIR /GAI_web

# Apt update and add app
RUN apt update && apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y

# Install time
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends tzdata
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# Install Chinese Language
RUN DEBIAN_FRONTEND=noninteractive apt install locales -y
RUN locale-gen en_US.utf8
ENV LANG=en_US.utf8 LC_ALL=en_US.utf8

# Install curl
RUN DEBIAN_FRONTEND=noninteractive apt install curl -y

# Install wget
RUN DEBIAN_FRONTEND=noninteractive apt install wget -y

# Install unzip
RUN DEBIAN_FRONTEND=noninteractive apt install unzip -y

# Install libldap
RUN DEBIAN_FRONTEND=noninteractive apt install build-essential python3.10-dev \
libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind -q -y

#Install ODBC package
RUN DEBIAN_FRONTEND=noninteractive apt update && apt install unixodbc unixodbc-dev -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN sh -c "echo 'deb [arch=amd64] https://packages.microsoft.com/ubuntu/20.04/prod focal main' > /etc/apt/sources.list.d/mssql-release.list"
RUN DEBIAN_FRONTEND=noninteractive apt update
RUN ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt install msodbcsql17 -y
RUN dpkg -l | grep msodbcsql

RUN DEBIAN_FRONTEND=noninteractive apt install libaio1 -y

# Install Python
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3.10 python3.10-distutils
RUN ln -sf /usr/bin/python3.10 /usr/bin/python
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Install pkg-config:
RUN apt install pkg-config

# Install cairo development libraries:
RUN apt install libcairo2-dev -y

# Install FFMPEG:
RUN apt install ffmpeg -y

# Copy application requirements file to the created working directory
WORKDIR  /GAI_web
COPY requirements.txt .

# Install application dependencies from the requirements file
RUN pip install setuptools==61.1.1
RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
RUN python -m pip install paddlepaddle-gpu==2.6.1.post112 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
RUN pip install -r requirements.txt

# Expose any necessary ports (if applicable)
EXPOSE 8501

# Run the python application
WORKDIR  /GAI_web

# Specify the default command to run when starting the container
CMD ["streamlit","run","rag_engine.py","--server.address","0.0.0.0","--server.port","8501"]
