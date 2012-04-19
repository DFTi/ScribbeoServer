#\ -s puma -p 3000
# Currently the port is hardcoded above, 
# for deploy though we'll want to use Settings.instance_port value

require './init'

if DEVELOPMENT
  require 'sass/plugin/rack'
  Sass::Plugin.options[:template_location] = 'app/views/stylesheets'
  Sass::Plugin.options[:css_location] = 'app/public/css'
  use Sass::Plugin::Rack
end

use Rack::Session::Cookie, :secret => 'scribbeo_cookie'
use Rack::MethodOverride

use Warden::Manager do |manager|
  manager.default_strategies :password
  manager.failure_app = App
end

map "/" do 
  run App
end
