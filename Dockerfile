FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set the working directory
WORKDIR /minivan

ARG DEBIAN_FRONTEND=noninteractive

# Install Conda
RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3.13 \
    && conda update conda \
    # && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH

# Install dependencies
RUN apt-get -qq update -y && \
    apt-get -qq -y install --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    make && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

ENV PYTHONPATH="/minivan/python:${PYTHONPATH}"

RUN conda init bash

COPY ./environment.yml /minivan/environment.yml
RUN conda env update --file /minivan/environment.yml --prune --name base && \
    conda clean --all --yes