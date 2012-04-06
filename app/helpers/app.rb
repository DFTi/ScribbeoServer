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
  
  def authorize_user!
    redirect '/login' if user.nil? 
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
end