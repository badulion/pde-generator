FROM continuumio/miniconda3

WORKDIR /workspace

RUN wget https://raw.githubusercontent.com/DedalusProject/dedalus_conda/master/conda_install_dedalus3.sh
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

COPY conda_install_dedalus3.sh .
RUN source conda_install_dedalus3.sh
RUN rm conda_install_dedalus3.sh

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY main.py .

COPY config/ ./config/
COPY src/ ./src/
