FROM odoo:18

# 🔥 CRITICAL: SET LOCALE TO UTF-8 - This is vital for Python string handling
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

USER root

# Install wkhtmltopdf, fontconfig (for font discovery), and Ethiopic fonts
RUN apt update && apt upgrade -y \
    && apt install -y fonts-sil-abyssinica fonts-sil-padauk locales

# Create necessary directories
RUN mkdir -p /etc/odoo/{themes,customs,etc}
RUN mkdir -p /opt/wkhtmltopdf/bin


# Copy configuration and custom modules/themes
COPY ./etc/odoo.conf /etc/odoo/odoo.conf
COPY ./customs /etc/odoo/customs
COPY ./themes /etc/odoo/themes

EXPOSE 8069

ENTRYPOINT ["odoo", "-c", "/etc/odoo/odoo.conf"]