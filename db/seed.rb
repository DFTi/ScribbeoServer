## 
# Seeds the database with initial values.
# Gets executed after migrations are complete.
def db_seed
  
  admin = User.create({
    :username=>"admin",
    :password=>"admin",
    :password_confirmation=>"admin"
  })
  admin.admin = true
  admin.save
  
  # Let's think about this.
  # Log.create({
  #   :title=>"entry"
  #   :log_level=>"info"
  #   :event=>"Seeded the database with default values."
  #   })

  # Java settings
  Settings.icon_path = File.join("images","ruby.png")

  # iOS Build
  Settings.ipa_path = "#{App.root}/../lib/iOS/scribbeo/Scribbeo.ipa"
  Settings.ipa_needs_manifest = true
  Settings.ipa_installs ||= 0
  Settings.ipa_version ||= ""

  # General Settings
  if DEVELOPMENT
    Settings.root_directory = "/Users/keyvan/Movies"
  else
    Settings.root_directory = "/home/curator/media"
  end
  
  Settings.instance_name = "My Scribbeo Server"
  
  Settings.instance_port = 9292
  Settings.bonjour_enabled = true

  # Security Settings
  Settings.ssl_enabled = true
  Settings.cert_path = File.join('ssl', 'default', 'cert')
  Settings.key_path = File.join('ssl', 'default', 'pkey')

  # Timecode & Transcode settings
  # false to disable, true for offline conversion, :live for live transcoding
  Settings.transcode = false 
  Settings.ffmbc_path = "/usr/local/bin/ffmbc"

  # Misc
  Settings.show_admin_password_hint = true

end