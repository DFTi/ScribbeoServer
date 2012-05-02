class App < Sinatra::Base
  # Description
  # ===========
  # Implements the legacy (Scribbeo) API
  # Extends it with user/folder stuff
  # Stores monolith note archive in the DB

  # Notes regarding database & filesystem
  # =====================================
  # Should actually just stay synchronized with the filesystem,
  # detecting & saving changes to the database. This way,
  # e.g. when timecode is generated, or a note is created,
  # we can associate that new metadata with the db entry.
  # It will also reduce filesystem burden & hasten response.
  # We'll save this stuff for Cruzzeo's API implementation.

  helpers do
    def entry_hash_for(type, entry, relpath)
      out = { 'name'=>entry }
      if type == :file
        if (ext = File.extname(entry)[1..-1]).nil?
          raise "File without extension" # dont send any junk!
        end
        out['ext'] = ext
        out['asset_url'] = File.join("", "asset", relpath, entry)
        out['live_transcode'] = "Not implemented" # TODO this.
      elsif type == :folder
        out['list_url'] = File.join("", "list", relpath, entry)
      end
      out
    end

    def path_from_splat(splat)
      relpath = splat[0]
      path_parts = relpath.split('/').compact.reject(&:blank?)
      virtual_folder = Folder.find_by_name(path_parts.delete_at(0))
      return File.join(virtual_folder.path, path_parts)
    end
  end

  get '/list*' do
    authorize_user!
    relpath = params[:splat][0]
    puts relpath.inspect
    res = {"files"=>[], "folders"=>[]}
    if base_url?(relpath) # Send virtual folders
      user.existent_folders.each do |f|
        res['folders'] << {
          "name" => f.name,
          "list_url" => File.join('', 'list', f.name)
        }
      end
    else # Send real files and folders
      path_parts = relpath.split('/').compact.reject(&:blank?)
      virtual_folder_id = Folder.find_by_name(path_parts.delete_at(0)).id
      virtual_folder = user.folders.find(virtual_folder_id)
      virtual_folder.entries(path_parts).each do |entry|
        file_path = File.join(virtual_folder.path, path_parts)
        if File.directory?(file_path)
          res["folders"] << entry_hash_for(:folder, entry, relpath)
        elsif File.exists?(file_path)
          res["files"] << entry_hash_for(:file, entry, relpath) rescue next
        end
      end
    end
    json(res)
  end

  get '/asset*' do
    authorize_user!
    asset_path = path_from_splat(params[:splat])
    if asset_path && File.exists?(asset_path)
      send_file(asset_path)
    else
      status 404
    end
  end

  get '/timecode/asset*' do
    authorize_user!
    asset_path = path_from_splat(params[:splat])
    # FIXME Move FFMBC / Timecode stuff into module(s)
    zeros = '00:00:00:00'    
    if asset_path && File.exists?(asset_path)
      # FIXME Should perform caching in larger systems
      details = Open3.popen3("#{Settings.ffmbc_path} -i '#{asset_path}'"){|i,o,e,t| p e.read.chomp }
      matches = details.match(/timecode: \d{2}:\d{2}:\d{2}:\d{2}/) # NDFTC
      if matches.nil?
        matches = details.match(/timecode: \d{2}:\d{2}:\d{2};\d{2}/) # DFTC
        matches.nil? ? zeros : matches[0][10..-1].gsub(';', ':') # TODO make client support DFTC notation
      else
        matches[0][10..-1]
      end
    else
      # Log the fact that we failed to get a timecode for bad asset path
      zeros
    end
  end

  get '/notes/asset*' do
    authorize_user!
    prefix = '+asset'+params[:splat][0].gsub('/', '+')
    # Much BS here (+'s) is due to client originally targeting the filesystem
    notes = []
    Upload.all_of_type("note").each do |n|
      if n.filename[0, prefix.length] == prefix
        notes << "/note/#{n.filename}" 
      end
    end
    json notes
  end

  get(multi_io_route = %r{^/(note|email|audio|avid|xml)/(.*)}) do
    authorize_user!
    if fakefile = Upload.find_by_filename(params[:captures][1])
      content_type 'application/x-binary' # may be optional
      fakefile.binary_data
    else
      status 404
    end
  end

  post multi_io_route do
    authorize_user!
    fakefile = user.uploads.find_by_filename(params[:captures][1])
    if fakefile.nil?
      fakefile = user.uploads.new do |f|
        f.filename = params[:captures][1]
        f.content_type = params[:captures][0]
      end
    end
    fakefile.binary_data = request.body.read
    json :success => fakefile.save
  end

end
