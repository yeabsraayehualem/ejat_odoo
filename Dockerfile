FROM odoo:18

USER root

# Create directories
RUN mkdir -p /etc/odoo/{themes,customs,etc}

# Copy configs and modules
COPY ./etc/odoo.conf /etc/odoo/odoo.conf
COPY ./customs /etc/odoo/customs
COPY ./themes /etc/odoo/themes

# RUN apt-get update && \
#     apt-get install -y fonts-noto fonts-noto-unhinted && \
#     fc-cache -f -v



EXPOSE 8069

ENTRYPOINT ["odoo", "-c", "/etc/odoo/odoo.conf"]
