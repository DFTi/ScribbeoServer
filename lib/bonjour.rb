# JRuby/MRI bonjour wrapper
# On windows, we need to make sure this is available, hopefully bonjour for windows makes it available
# https://developer.apple.com/library/mac/#documentation/Java/Reference/DNSServiceDiscovery_JavaRef/com/apple/dnssd/DNSSD.html
class Bonjour
  attr_accessor :name, :port

  if RUBY_PLATFORM == 'java'
    import com.apple.dnssd.DNSSD # TODO find out what happens if we're on windows without bonjour available
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
    @port = port
    @running = false
    @service = false
    start unless invalid?
  end

  def start
    return false if invalid?
    if RUBY_PLATFORM == 'java'
      @service = DNSSD.register(@name, "_videoTree._tcp", @port.to_i, BonjourListener.new)
    else
      @service = DNSSD.register(@name, "_videoTree._tcp", nil, @port.to_i)
    end
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

end