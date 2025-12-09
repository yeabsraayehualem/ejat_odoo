clear
docker compose down && docker compose up -d --build
sleep 2
docker exec -it ejat_odoo-web-1 tail -f /etc/odoo/odoo-server.log