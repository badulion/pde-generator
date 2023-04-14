FROM python:3.10-bullseye

WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY solver.py .
COPY eq_generator.py .
COPY eq_wrapper.py .
COPY initial.py .

COPY config/ ./config/
COPY utils/ ./utils/
