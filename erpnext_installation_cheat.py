bench init frappe-bench-14 --frappe-branch version-14

bench get-app erpnext --branch version-14

Install 
Public: 
bench get-app branch
bench get-app  https://github.com/frappe/ecommerce_integrations
bench get-app  https://github.com/frappe/education
bench get-app https://github.com/frappe/hrms

bench --site <site> install-app <app>

Github password: Jglory!1 --updated 11/06/2024
Private: 
bench get-app https://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@github.com/NextServ/phbir --branch jeff-branch
bench get-app https://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@github.com/NextServ/weekly_planner --branch jeff-branch
bench get-app https://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@github.com/NextServ/sms --branch jeff-branch
bench get-app https://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@github.com/NextServ/schoolext --branch jeff-branch

bench --site <site> install-app <app>


bench setup production jeffchavezdev 
- when require superuser prefix with sudo

Port based multitenancy - https://frappeframework.com/docs/user/en/bench/guides/setup-multitenancy

Switch off DNS based multitenancy (once) - bench config dns_multitenant off
Create a new site - bench new-site site2name
Set port - bench set-nginx-port site2name 82
Re generate nginx config - bench setup nginx
Reload nginx - sudo service nginx reload

Add this to /sites common_site_config.json
{
 "developer_mode": 1,
 "disable_website_cache": true,
 "http_timeout": 86400,
 "mute_emails": true,
 "pause_scheduler": 0,
 "server_script_enabled": false,
}

bench --site aos.erp.local restore manual-backups/database.sql --with-public-files manual-backups/public.tar --with-private-files manual-backups/private.tar

bench update --no-backup

bench --site { site } migrate

bench --site dcode.com install-app erpnext

*After creating the site return to the step in multi-tenancy. 

20001
20002


