Warden::Manager.serialize_into_session{|user| user.id }
Warden::Manager.serialize_from_session{|id| User.find_by_id(id) }

Warden::Manager.before_failure do |env,opts|
  env['REQUEST_METHOD'] = "POST"
end

Warden::Strategies.add(:password) do
  def valid?
    params["username"] || params["password"]
  end 

  def authenticate!
    if u = User.authenticate(params["username"], params["password"])
      u.track request
      success!(u)
    else
      fail!("Could not log in")
    end
  end 
end