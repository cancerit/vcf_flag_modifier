FROM python:3.6-alpine

# Add service user
ENV USER=service
ENV HOME=/opt/wtsicgp


RUN mkdir -p $HOME
RUN addgroup $USER && \
    adduser -G $USER -D -h $HOME $USER
WORKDIR $HOME

# Temporarily install alpine linux dependencies for building python, ruby and alpine linux dependencies
RUN apk add --no-cache --virtual build-deps gcc python3-dev musl-dev build-base linux-headers
# Install alpine linux dependencies
RUN apk add --no-cache bash ruby ruby-dev
# Install pysam dependency
RUN apk add --no-cache libstdc++ bzip2-dev xz-dev zlib-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR $HOME

# Copy over source code
COPY ./ .
RUN pip install ./

RUN apk del build-deps ruby-dev

RUN chown -R $USER:$USER .

# Become the final user
USER service

CMD python vcf_flag_modifier.py
