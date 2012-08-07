class App < Sinatra::Base
  MOBILECONF = {
    :mime_type => "application/x-apple-aspen-config; charset=utf-8",
    :template => File.join(App.root, '..', "/lib/iOS/Profile.mobileconfig"),
    :outfile => File.join(App.root, '..', "/tmp/Profile.mobileconfig")
  }

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
    udid_store_route = request.url+"/new_enrollment?udid=#{udid}"
    redirect to(udid_store_route), 301
  end

  get '/enroll/mobileconfig/parse/new_enrollment' do
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


  get '/install' do
    erb :install
  end

  get "/install/manifest.plist" do
    Build.write_manifest(request)
    send_file Build.manifest_path
  end
  
  
  get '/install/manifest.plist/Scribbeo.ipa' do
    Settings.ipa_installs += 1
    send_file Settings.ipa_path, :type=>'application/octet-stream ipa'
  end

end
