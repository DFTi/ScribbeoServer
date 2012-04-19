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
    @error = "Invalid credentials."
    erb :login
  end
end
