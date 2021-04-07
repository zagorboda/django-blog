FROM nginx:1.19.0-alpine

RUN mkdir /nginx
RUN mkdir /nginx/static/
WORKDIR /nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d