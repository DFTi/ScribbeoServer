require_relative '../lib/certgen'

## 
# Seeds the database with initial values.
# Gets executed after migrations are complete.
def db_seed
  
  User.create({
    :username=>"admin",
    :password=>"admin",
    :password_confirmation=>"admin"
  })

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
  ## Autogenerate default certs into database
  certs = CertGen.new_credentials
  Settings.ssl_cert = certs[0]
  Settings.ssl_key = certs[1]
  # We'll dump them to a file on first run if deploy server needs it that way.
  Settings.use_db_cert = true # toggle to enable using the user cert paths below
  Settings.user_cert_path = ""
  Settings.user_key_path = ""

  # Timecode & Transcode settings

  # false to disable, true for offline conversion, :live for live transcoding
  Settings.transcode = false 
  Settings.ffmbc_path = ""

end