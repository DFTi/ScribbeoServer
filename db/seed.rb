## 
# Seeds the database with initial values.
# Gets executed after migrations are complete.
def db_seed
  
  User.create({
    :username=>"admin",
    # :admin=>true,
    :password=>"admin",
    :password_confirmation=>"admin"
  })

  # Let's think about this.
  # Log.create({
  #   :title=>"entry"
  #   :log_level=>"info"
  #   :event=>"Seeded the database with default values."
  #   })

  # Java settings
  Settings.icon_path = File.join("images","ruby.png")

  # iOS Build
  Settings.ipa_path = ""

  # General Settings
  Settings.root_directory = "/home/curator/media"
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