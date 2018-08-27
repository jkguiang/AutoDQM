FROM cern/cc7-base
EXPOSE 443

RUN yum update -y && yum install -y \
      ImageMagick \
      httpd \
      mod_ssl \
      npm \
      openssl \
      php \
      python2-pip \
      root-python \
      shibboleth \
      xmltooling-schemas \
      opensaml-schemas \
      curl-openssl

# CERN Shibboleth SSO files
RUN cd /etc/shibboleth && \
      curl -O http://linux.web.cern.ch/linux/centos7/docs/shibboleth/shibboleth2.xml && \
      curl -O http://linux.web.cern.ch/linux/centos7/docs/shibboleth/ADFS-metadata.xml && \
      curl -O http://linux.web.cern.ch/linux/centos7/docs/shibboleth/attribute-map.xml && \
      curl -O http://linux.web.cern.ch/linux/centos7/docs/shibboleth/wsignout.gif
RUN chmod 777 /etc/shibboleth/shibboleth2.xml

# Python requirements
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

# Install create-react-app dependencies
WORKDIR /webapp
COPY webapp/package.json /webapp/package.json
RUN npm install

# Produce a production build of the frontend
COPY webapp /webapp
RUN npm run build
RUN cp -r /webapp/build /var/www/public

# Secrets directory
RUN mkdir /db /run/secrets
RUN chown -R apache:apache /db /var/www /run/secrets

# Attach apache logs to docker logs
RUN ln -s /dev/stdout /etc/httpd/logs/access_log
RUN ln -s /dev/stderr /etc/httpd/logs/error_log

# Set AutoDQM env vars
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-bundle.crt
ENV ADQM_SSLCERT /run/secrets/cmsvo-cert.pem
ENV ADQM_SSLKEY /run/secrets/cmsvo-cert.key
ENV ADQM_DB /db/
ENV ADQM_PUBLIC /var/www/
ENV ADQM_CONFIG /var/www/public/config/
ENV ADQM_PLUGINS /var/www/cgi-bin/plugins/

# Apache configuration files
COPY httpd/httpd.conf /etc/httpd/conf/httpd.conf
COPY httpd/htaccess /var/www/.htaccess

# Backend sources and configuration
COPY index.py /var/www/cgi-bin/index.py
COPY autodqm /var/www/cgi-bin/autodqm
COPY autoref /var/www/cgi-bin/autoref
COPY plugins /var/www/cgi-bin/plugins
COPY config /var/www/public/config

# Run command
COPY httpd/start.sh ./
RUN chmod 751 ./start.sh
CMD ./start.sh

