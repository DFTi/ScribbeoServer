class App < Sinatra::Base

  namespace '/admin' do
    before do
      authorize_admin!
      @title = "Admin"
      request.instance_eval { def secure?; true; end } if PRODUCTION
    end

    get "/dashboard" do
      @users = User.all_but_admin
      @folders = Folder.all
      erb :admin
    end

    namespace '/user' do
      post '/create' do
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

      # Delete files through web interface
      post '/:id/contents/:filename/delete' do
        folder = Folder.find(params[:id])
        res = File.basename(FileUtils.rm(File.join(folder.path, params[:filename]))[0]) rescue false
        json({
          "success"=>res ? true : false,
          "filename"=>params[:filename],
          "file_deletion"=>true
        })
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

  end

end
