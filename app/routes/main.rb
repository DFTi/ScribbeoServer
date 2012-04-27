class App < Sinatra::Base
  get "/" do
    if user
      redirect '/admin/dashboard'
    else  
      redirect '/login'
    end
  end

  if DEVELOPMENT
    get '/env' do 
      my_env = {}
      env.each do |k,v|
        v = v.to_s if v.class != String
        my_env[k] = v 
      end
      json(my_env)
    end
  end

end
