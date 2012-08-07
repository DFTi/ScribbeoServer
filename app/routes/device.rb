class App < Sinatra::Base

  MOBILECONF = {
    :mime_type => "application/x-apple-aspen-config; charset=utf-8",
    :template => File.join(App.root, '..', "/lib/iOS/Profile.mobileconfig"),
    :outfile => File.join(App.root, '..', "/tmp/Profile.mobileconfig")
  }

  MANIFEST = {
    :template => File.join(App.root, '..', "/lib/iOS/manifest.plist"),
    :url_prefix => "itms-services://?action=download-manifest&url=",
    :ipa_url => "[IPAURL]"
  }

  get '/enroll' do
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
    @device = Device.new
    @udid = params["udid"]
    erb :new_device
  end

  get "/install" do
    if File.exists? Settings.ipa_path
      "Build installer"
    else
      "A build has not been created yet."
    end
  end



end
