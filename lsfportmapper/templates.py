from jinja2 import Template

frontend=Template("""
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
