# RACK_ENV=production puma -b 'ssl://0.0.0.0:9292?key=config/ssl/pkey&cert=config/ssl/cert'
# We're actually set up behind a apache vhost proxy with SSL, so just run
puma
