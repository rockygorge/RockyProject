FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html app.js style.css /usr/share/nginx/html/
USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
