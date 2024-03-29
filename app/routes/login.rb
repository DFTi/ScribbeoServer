class App < Sinatra::Base
  
  get '/login/?' do
    erb :login
  end

  post '/login/?' do
    env['warden'].authenticate!
    redirect "/"
  end

  get '/logout/?' do
    env['warden'].logout
    redirect '/'
  end

  post '/unauthenticated/?' do
    status 401
    @error = "Invalid credentials. <a href='/'>Try again?</a>"
  end

  get '/hide_admin_password_hint' do
    Settings.show_admin_password_hint = false
    redirect '/login'
  end

end
