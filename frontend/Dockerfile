FROM nginx:1.27-alpine

ARG API_BASE=/api

COPY src /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

RUN sed -i "s|__API_BASE__|${API_BASE}|g" /usr/share/nginx/html/js/config.js

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
