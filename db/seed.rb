## 
# Seeds the database with initial values.
# Gets executed after migrations are complete.
def db_seed
  
  User.create({
    :username=>"admin",
    :password=>"admin",
    :password_confirmation=>"admin"
  })

  # Java settings
  Settings.icon_path = "images/ruby.png"

  # General Settings

  if ((system_user = ENV["USER"]) && system_user.size > 1)
    Settings.instance_name = "#{system_user}'s Scribbeo Server"
  else
    Settings.instance_name = "My Scribbeo Server"
  end

  
  Settings.instance_port = 9042
  Settings.bonjour_enabled = true

  # Security Settings
  Settings.ssl_enabled = true
  Settings.cert_path = File.join('ssl', 'default', 'cert')
  Settings.key_path = File.join('ssl', 'default', 'pkey')

  # Timecode & Transcode settings
  # false to disable, true for offline conversion, :live for live transcoding
  Settings.transcode = false 
  Settings.ffmbc_path = "(stub)"

end