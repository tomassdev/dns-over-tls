FROM python:3.13.5-slim-bookworm

# Create a system user 'dot' to run the application
RUN useradd -r -m -s /sbin/nologin dot

# Set the working directory for the application
WORKDIR /home/dot

# Copy the application code and set ownership to 'dot' user
COPY --chown=dot:dot dot_proxy.py .

# Switch to the non-root user
USER dot

# Expose the application port
EXPOSE 53

# Run the Python application in unbuffered mode for real-time logging
CMD ["python", "-u", "dot_proxy.py"]
