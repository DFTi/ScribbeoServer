# JRuby/MRI bonjour wrapper
# On windows, we need to make sure this is available, hopefully bonjour for windows makes it available
# https://developer.apple.com/library/mac/#documentation/Java/Reference/DNSServiceDiscovery_JavaRef/com/apple/dnssd/DNSSD.html
class Bonjour
  def name=(name="")
    if name.size > 0
      @name = name
      announce if @running
      return true
    else
      return false
    end
  end

  def port=(port=0)
    port = port.to_i
    if port > 0
      @port = port
      announce if @running
      return true
    else
      return false
    end
  end

  if RUBY_PLATFORM == 'java'
    import com.apple.dnssd.DNSSD
    class BonjourListener
      def serviceRegistered(*args)
        # warn args.inspect
        # warn "Service successfully registered."
        return true
      end
      def serviceFound(*args)
        # puts args[3]
      end
    end
  end

  def initialize(name=nil, port=nil)
    @name = name
    @port = port.to_i
    @running = false
    @service = false
    announce
  end

  def announce
    return false if invalid?
    stop if @running
    if RUBY_PLATFORM == 'java'
      @service = DNSSD.register(@name, "_videoTree._tcp", @port.to_i, BonjourListener.new)
    else
      @service = DNSSD.register(@name, "_videoTree._tcp", nil, @port.to_i)
    end
    @running = true
    return true
  end
  
  def invalid?
    @name.nil? || @port.nil? || @port.to_i == 0
  end

  def stop
    return nil if @service.nil?
    @service.stop
    @running = false
    return true
  end

  def running?
    @running
  end

end