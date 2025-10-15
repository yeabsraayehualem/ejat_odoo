FROM odoo:18

USER root

RUN mkdir -p /etc/odoo/{themes,customs,etc}

COPY ./etc/odoo.conf /etc/odoo/odoo.conf
COPY ./customs /etc/odoo/customs
COPY ./themes /etc/odoo/themes

EXPOSE 8069

ENTRYPOINT ["odoo", "-c", "/etc/odoo/odoo.conf"]
