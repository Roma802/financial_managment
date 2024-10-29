FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
# COPY /home/web-app/app/staticfiles /usr/share/nginx/html/staticfiles
# RUN nginx -s reload
#CMD ["nginx", "-g", "daemon off;"]
