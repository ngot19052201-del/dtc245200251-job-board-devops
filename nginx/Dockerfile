FROM nginx:1.25-alpine

# Remove default configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom reverse proxy configuration and SSL certificates
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY ssl/ /etc/nginx/ssl/

# Expose HTTP and HTTPS ports
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
