module AppHelper
  def user
    env['warden'].user
  end

  def errors_for(r)
    r.errors.full_messages.join('<br>')
  end
  
  def img(filepath, html_opts={})
    options = html_opts.collect{|k,v| "#{k.to_s}='#{v}'"}.join(' ')
    %{<img src="#{url('/img/')}#{filepath}" #{options}/>}
  end
  
  def authorize_user!(redirect=false)
    if user.nil? 
      throw :halt, [ 401, 'Authorization Required' ]
    end
  end

  def authorize_admin!(redirect=false)
    if user.nil? || !user.admin?
      throw :halt, [ 401, 'Authorization Required' ]
    end
  end
  
  def partial(sym, locals={})
    erb(sym, :layout=>false, :locals=>locals)
  end
  
  def div(body, html_opts={})
    if body.class == Hash
      html_opts = body
      body = ''
    end
    options = html_opts.collect{|k,v| "#{k}='#{v}'"}.join(' ')
    %{<div #{options}>#{body}</div>}
  end

  def a(href, body, html_opts={})
    options = html_opts.collect{|k,v| "#{k}='#{v}'"}.join(' ')
    %{<a href="#{href}" #{options}>#{body}</a>}
  end

  # Useful for checking routes ending with a single *
  def base_url?(splat)
    splat.nil? || splat == '/' || splat == ''
  end

  def ios_toggle_button(opts)
    %{<div class="switch #{'on' if opts[:on_if]}" data-url="#{opts[:url]}">
        <span class="thumb"></span>
        <input #{'checked="yes"' if opts[:on_if]} type="checkbox" />
      </div>
      <div class="padding" style="height:20px"></div>}
  end

  def save_edit(opts)
    %{<input type="text" value="#{opts[:text]}">
      <button class="save" data-url="#{opts[:url]}">Save</button>}
  end

  def port_open?(port)
    s = Socket.new(Socket::AF_INET, Socket::SOCK_STREAM, 0)
    begin
      in_addr = Socket.pack_sockaddr_in(port.to_i, "0.0.0.0")
      s.bind(in_addr)
      s.close
      true
    rescue
      false
    end
  end
end