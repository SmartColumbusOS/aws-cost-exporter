FROM python:alpine3.7

RUN pip install pipenv

ADD Pipfile* /

RUN pipenv lock --requirements > requirements.txt \
  && pip install --requirement requirements.txt

ADD aws_cost_exporter.py /

CMD [ "python", "./aws_cost_exporter.py" ]
