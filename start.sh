#!/bin/sh

# Set the hostname of the shibboleth configuration to match the certificate
hn="$(openssl x509 -noout -subject -in ${ADQM_SSLCERT} | sed -n '/^subject/s/^.*CN=//p')"
sed -i "s/somehost\.cern\.ch/${hn}/g" /etc/shibboleth/shibboleth2.xml

# Start the Shibboleth daemon
shibd

# Start apache in the foreground
httpd -D FOREGROUND

