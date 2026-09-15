FROM dbeaver/cloudbeaver:latest

# Set working directory
WORKDIR /opt/cloudbeaver

# Create workspace directory
RUN mkdir -p /opt/cloudbeaver/workspace/.data

# Copy pre-configured datasource
COPY datasources.json /opt/cloudbeaver/workspace/.data/

# Set permissions
RUN chmod -R 777 /opt/cloudbeaver/workspace

# Expose port
EXPOSE 8978

# Start CloudBeaver
CMD ["./run-server.sh"]
