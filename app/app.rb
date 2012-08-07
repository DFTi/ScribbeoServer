class App < Sinatra::Base 
  configure do
    register Sinatra::Reloader if DEVELOPMENT
    register Sinatra::Namespace
  end
  before { @title = "ScribbeoServer"}
  
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
  
end

require_relative 'models/init'
require_relative 'helpers/init'
require_relative 'routes/init'