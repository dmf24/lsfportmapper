from jinja2 import Template

old_template=Template("""
server {
       listen 80;
       server_name {{ name }}.{{ domain }};
       location / {
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto http;
                proxy_set_header X-NginX-Proxy true;
                proxy_set_header Host $http_host;
                proxy_pass http://{{ endpoint }};
                proxy_redirect off;

                # WebSocket support
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 86400;
       }
}
""")

frontend=Template("""
server {
        listen 80;
        server_name {{ name }}.{{ domain }};
        rewrite ^(.*)$ https://$host$1 permanent;
}
server {
        listen 443;
        server_name {{ name }}.{{ domain }};

        ssl on;
        ssl_certificate /etc/ssl/certs/med.harvard.edu/*.med.harvard.edu.crt;
        ssl_certificate_key /etc/ssl/certs/med.harvard.edu/*.med.harvard.edu.key;

        ssl_session_timeout 5m;

        ssl_protocols TLSv1.1 TLSv1.2;
        ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kE
DH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES2
56-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK';
        ssl_prefer_server_ciphers on;

       location / {
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto http;
                proxy_set_header X-NginX-Proxy true;
                proxy_set_header Host $http_host;
                proxy_pass http://{{ endpoint }};
                proxy_redirect off;

                # WebSocket support
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 86400;
       }
}
""")
