#\ -p 3000
# Currently the port is hardcoded above, 
# for deploy though we'll want to use Settings.instance_port value

require './init'

if DEVELOPMENT
  require 'sass/plugin/rack'
  Sass::Plugin.options[:template_location] = 'app/views/stylesheets'
  Sass::Plugin.options[:css_location] = 'app/public/css'
  use Sass::Plugin::Rack
end


#require 'rack/raw_upload'
#use Rack::RawUpload
#use Rack::Encryption ??

# require 'rack/contrib'

# Rack::NestedParams #- parses form params with subscripts (e.g., * “post[title]=Hello”) into a nested/recursive Hash structure (based on Rails’ implementation).
# Rack::Evil #- Lets the rack application return a response to the client from any place.
# Rack::Signals #- Installs signal handlers that are safely processed after a request
# Rack::Callbacks #- Implements DSL for pure before/after filter like Middlewares.
# Rack::Config #- Shared configuration for cooperative middleware.
# Rack::Deflect #- Helps protect against DoS attacks.
# Rack::ResponseCache #- Caches responses to requests without query strings to Disk or a user provider Ruby object. Similar to Rails’ page caching.
# Rack::RelativeRedirect #- Transforms relative paths in redirects to absolute URLs.
# Rack::Access #- Limits access based on IP address

# class MyMiddleware
#   def initialize(app)
#     @app = app
#   end

#   def call(env)
#     status, headers, body = @app.call(env)
#     return [status, headers, body]
#   end
# end

# use MyMiddleware

use Rack::Session::Cookie, :secret => 'scribbeo_cookie'
use Rack::MethodOverride

use Warden::Manager do |manager|
  manager.default_strategies :password
  manager.failure_app = App
end

map "/" do 
  run App
end
