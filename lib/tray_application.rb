require 'java'
require 'rubygems'
require 'launchy'

class TrayApplication

  include Java
  import java.awt.TrayIcon
  import java.awt.Toolkit

  attr_accessor :icon_filename
  attr_accessor :menu_items

  def initialize(name = 'Tray Application', icon_path=nil)
    @menu_items = []
    @name = name
    @icon_filename = icon_path if icon_path
  end

  def item(label, &block)
    item = java.awt.MenuItem.new(label)
    item.add_action_listener(block)
    @menu_items << item
  end

  def run
    @popup = java.awt.PopupMenu.new
    @menu_items.each{|i| @popup.add(i)}

    # Give the tray an icon and attach the popup menu to it
    image = java.awt.Toolkit::default_toolkit.get_image(@icon_filename)
    @tray_icon = TrayIcon.new(image, @name, @popup)
    @tray_icon.image_auto_size = true

    # Finally add the tray icon to the tray
    tray = java.awt.SystemTray::system_tray
    tray.add(@tray_icon)
  end

end
