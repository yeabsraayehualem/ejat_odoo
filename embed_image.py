import base64
import os

image_path = '/home/yeab/Desktop/ejat/ejat_odoo/customs/badge_maker/static/img/idfront.png'
xml_path = '/home/yeab/Desktop/ejat/ejat_odoo/customs/badge_maker/views/badge_report.xml'

with open(image_path, 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')

with open(xml_path, 'r') as xml_file:
    content = xml_file.read()

# Target string to replace
target = 'src="/badge_maker/static/img/idfront.png"'
replacement = f'src="data:image/png;base64,{b64_string}"'

if target in content:
    new_content = content.replace(target, replacement)
    with open(xml_path, 'w') as xml_file:
        xml_file.write(new_content)
    print("Successfully embedded base64 image.")
else:
    print("Target string not found in XML.")
