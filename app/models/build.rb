class Build # < ActiveRecord::Base
  # belongs_to :app
  # mount_uploader :ipa, IpaUploader

  MANIFEST = {
    :template => File.join(App.root, '..', "/lib/iOS/manifest.plist"),
    :ipa_url => "[IPAURL]"
  }

  def self.write_manifest(request)
    # return if !Settings.ipa_needs_manifest
    File.open(File.join(App.root, "../tmp/manifest.plist"), "w") do |f|
      File.open(MANIFEST[:template], "r") do |tmpl|
        f.write tmpl.read.gsub("[IPAURL]", "#{request.url}/Scribbeo.ipa")
      end
    end
    # Settings.ipa_needs_manifest = true
  end

  def self.install_link(request)
    "itms-services://?action=download-manifest&url=#{request.url}/manifest.plist"
  end

  def self.manifest_path
    File.join(App.root, "../tmp/manifest.plist")
  end

end
