FROM alfg/nginx-rtmp:latest

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose RTMP and HTTP ports
EXPOSE 1935 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]