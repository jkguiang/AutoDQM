FROM cern/cc7-base
EXPOSE 80

RUN yum update -y && yum install -y \
      ImageMagick \
      httpd \
      php \
      root-python

RUN mkdir /db /run/secrets
RUN chown -R apache:apache /db /var/www /run/secrets

ENV ADQM_CONFIG /var/www/public/configs.json
ENV ADQM_DB /db/
ENV ADQM_TMP /var/www/tmp/
ENV ADQM_SSLCERT /run/secrets/cmsvo-cert.pem
ENV ADQM_SSLKEY /run/secrets/cmsvo-cert.key

COPY httpd.conf /etc/httpd/conf/httpd.conf
COPY public /var/www/public
COPY src /var/www/cgi-bin
COPY configs.json /var/www/public/configs.json

CMD ["/usr/sbin/httpd","-D","FOREGROUND"]

