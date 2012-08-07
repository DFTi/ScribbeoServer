class App < Sinatra::Base
  get "/enroll" do
    "UDID Extractor"
  end
  
  get "/install" do
    if File.exists? Settings.ipa_path
      "Build installer"
    else
      "A build has not been created yet."
    end
  end
end
