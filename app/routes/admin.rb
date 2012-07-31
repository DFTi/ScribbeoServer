class App < Sinatra::Base

  namespace '/admin' do 
    before do
      @title = "Admin"
      authorize_user!
      request.instance_eval { def secure?; true; end } if PRODUCTION
    end
    
    get "/dashboard" do
      @users = User.all_but_admin
      @folders = Folder.all
      erb :admin
    end

    namespace '/user' do
      post '/create' do
        authorize_user!
        user = User.new.with_password(params[:user])
        json({
          "success"=>user.save,
          "errors"=>errors_for(user),
          "html"=>partial(:user, :user=>user)
        })
      end
    
      post '/destroy' do
        json({
          "success"=>(User.destroy(params[:id]) ? true : false),
          "id"=>params[:id]
        })
      end

      post '/change_password' do
        # Users should not have to be admins to do this.
        # Right now there are no roles (users are "admins")
        json({
          "success"=>(env['warden'].user.change_password(params[:user]))
        })
      end
    end
    
    namespace "/folder" do      
      get '/index.html.json' do 
        folders = Folder.all
        json({
          "html"=>partial(:folders, :folders=>folders)
        })
      end

      post '/create' do
        folder = Folder.new(params[:folder])
        json({
          "success"=>folder.save,
          "errors"=>errors_for(folder),
          "html"=>partial(:folder, :folder=>folder)
        })
      end
    
      post '/destroy' do
        json({
          "success"=>(Folder.destroy(params[:id]) ? true : false),
          "id"=>params[:id]
        })
      end

      get '/:id/contents' do
        @folder = Folder.find(params[:id])
        if @folder && @folder.exists?
          erb(:folder_contents)
        else
          "Folder does not exist on the filesystem"
        end
      end

      post '/:id/upload' do
        unless params[:file] &&
          (tmpfile = params[:file][:tempfile]) &&
          (name = params[:file][:filename])
          @error = "No file selected"
          return "No file selected"
        end
        @folder = Folder.find(params[:id])
        STDERR.puts "Uploading file, original name #{name.inspect}"
        path = File.join(@folder.path, name)
        File.open(path, "w") do |f|
          while blk = tmpfile.read(65536)
            f.write(blk)
          end
        end
        @notice="Uploaded!"
        erb(:folder_contents)
      end


    end
    
    namespace '/permission' do
      post '/set' do
        u = User.find(params[:user_id])
        f = Folder.find(params[:folder_id])
        json(f.add_user(u).merge({
          'html'=>partial(:folder, :folder=>f)
        }))
      end

      post '/unset' do
        u = User.find(params[:id])
        f = Folder.find(params[:folder_id])
        json(f.remove_user(u).merge({
          'count'=>f.users.count,
          'id'=>f.id,
          'user_id'=>u.id
        }))
      end
    end

    namespace '/settings' do 
      post '/bonjour/?' do
        if params['checked'] == "true" # on
          BONJOUR.announce
        else
          BONJOUR.stop
        end
        Settings.bonjour_enabled = BONJOUR.running?
      end

      post '/instance_name/?' do
        res = {}
        value = params["value"]
        if (value.size > 0)
          Settings.instance_name = value
          BONJOUR.name = value
          res["success"] = true
        else
          res["success"] = false
          res["errors"] = "Instance name can't be blank"
        end
        res["instance_name"] = Settings.instance_name
        json(res)
      end

      post '/instance_port/?' do
        res = {}
        value = params["value"]
        if (port_open?(value))
          Settings.instance_port = value

          # Restart required for changes to take effect, so not setting bonjour
          # On restart we will start rack & bonjour with Settings.instance_port

          res["success"] = true
          res["notice"] = "Change will take effect after restart"

          # FIXME perhaps we can initiate a redirect to the new port after binding
          # lets look into server restarting, e.g. rack server control from sinatra (or java)

        else
          res["success"] = false
          res["errors"] = "Could not bind on port #{value}."
        end
        res["instance_port"] = Settings.instance_port
        json(res)
      end
    end

  end

end
