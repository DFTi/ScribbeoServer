class App < Sinatra::Base
  get '/devices/enroll' do
    @ios_request = (request.user_agent =~ /(Mobile\/.+Safari)/)
    erb :enroll
  end

  get '/enroll/mobileconfig' do
    plist_parse_route = request.url+"/parse"
    File.open(MOBILECONF[:outfile], "w") do |out|
      File.open(MOBILECONF[:template], "r") do |tmpl|
        out.write tmpl.read.gsub('[NextURL]', plist_parse_route)
      end
    end
    send_file MOBILECONF[:outfile], :type => MOBILECONF[:mime_type]
  end

  post '/enroll/mobileconfig/parse' do
    udid = request.body.read.match(/<string>([a-zA-Z0-9]+)<\/string>/)[1]
    udid_store_route = request.url+"/store?udid=#{udid}"
    redirect to(udid_store_route), 301
  end

  get '/enroll/mobileconfig/parse/store' do
    @udid = params["udid"]
    erb :new_device
  end

  post '/devices/save' do
    @device = Device.new(params[:device])
    if @device.save
      "Your device information has been saved."
    else
      "Could not save, try hitting the back button and checking the form."
    end
  end

  get '/devices' do
    authorize_admin!
    @devices = Device.all
    @enroll_url = request.url+"/enroll"
    erb :devices
  end


  get "/install" do
    "Not yet implemented"
    # if File.exists? Settings.ipa_path
    #   manifest_path = "#{Rails.root}/tmp/manifest.plist"
    #   File.open(manifest_path, "w") do |f|
    #     f.write self.app.manifest.gsub('[NextURL]', ipa_app_build_url(self.app, self, :host=>HOST, :port=>PORT))
    #   end
    #   send_file manifest_path
    # else
    #   "A build has not been created yet."
    # end
  end

end
