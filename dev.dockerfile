ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION

# install all development dependencies
COPY dev-requirements.txt /home/
RUN pip install -r /home/dev-requirements.txt
