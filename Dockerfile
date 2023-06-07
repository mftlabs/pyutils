FROM --platform=linux/amd64 centos:centos7.9.2009 as builder
MAINTAINER "MFTLABS"
WORKDIR /apps
RUN yum -y update; yum clean all
RUN yum -y install sudo epel-release; yum clean all
#RUN yum -y install python3-dev libsasl2-dev libldap2-dev libssl-dev
RUN  yum install -y net-tools wget perl-core zlib-devel wget && yum -y groups mark install "Development Tools" && yum -y groups mark convert "Development Tools" && yum -y groupinstall "Development Tools" && yum install -y openssl-devel && yum install -y libffi-devel && yum clean all
RUN wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz && tar -xvf Python-3.8.5.tgz && cd Python-3.8.5 && ./configure --enable-optimizations && make altinstall && cd .. && rm -rf Python-3.8.5.tgz && rm -rf Python-3.8.5
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py && rm -rf get-pip.py
RUN pip3.8 install --upgrade pip
RUN pip3.8 install --upgrade setuptools
RUN pip3.8 install --upgrade wheel
RUN pip3.8 install --upgrade pyyaml
RUN pip3.8 install --upgrade requests
RUN pip3.8 install --upgrade jinja2
RUN pip3.8 install --upgrade attrdict
RUN yum install gtk3-devel -y
RUN yum install which -y
RUN pip3.8 install --upgrade pytz
RUN pip3.8 install --upgrade paramiko
RUN pip3.8 install --upgrade pysftp
RUN pip3.8 install --upgrade ldap3
RUN pip3.8 install --upgrade robotframework
RUN pip3.8 install --upgrade robotframework-sshlibrary
RUN pip3.8 install --upgrade robotframework-seleniumlibrary
RUN pip3.8 install --upgrade robotframework-requests
RUN pip3.8 install --upgrade robotframework-httplibrary
RUN pip3.8 install --upgrade robotframework-archivelibrary
RUN pip3.8 install --upgrade robotframework-difflibrary
RUN pip3.8 install --upgrade robotframework-jsonlibrary
RUN pip3.8 install --upgrade httplib2
RUN pip3.8 install --upgrade beautifulsoup4
RUN pip3.8 install --upgrade splinter
#RUN pip3.8 install --upgrade python-ldap
RUN pip3.8 install --upgrade cx_oracle
RUN pip3.8 install --upgrade db2
RUN pip3.8 install --upgrade automagica
RUN useradd -u 1010 mftadmin && usermod -aG wheel mftadmin
RUN echo "mftadmin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "mftadmin:@Dmin123" | chpasswd
RUN unlink /usr/bin/python && ln -s  /usr/local/bin/python3.8 /usr/bin/python
USER mftadmin
CMD ["/bin/bash", "-c", "--", "while true; do sleep 30; done;"]
#RUN pip3.8 install --upgrade robotframework-ride
#RUN mkdir -p /apps/install/robotframework && cd /apps/install/robotframework && git clone https://github.com/robotframework/RIDE.git && cd RIDE && pip3.8 install -r requirements.txt




