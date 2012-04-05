RubyPackager::ReleaseInfo.new.
 author(
   :name => 'Keyvan Fatehi',
   :email => 'keyvan@digitalfilmtree.com',
   :web_page_url => 'http://digitalfilmtree.com'
 ).
 project(
   :name => 'ScribbeoRubyServer',
   :web_page_url => 'http://scribbeo.com',
   :summary => 'Server backend for the Scribbeo iOS application.',
   :description => 'Hybrid desktop/web application with an administration panel enabling an administrator to share multiple folders of multimedia with users on a network. Users will stream the multimedia over HTTP/S.',
   :image_url => '',
   :favicon_url => '',
   :browse_source_url => '',
   :dev_status => 'Beta'
 ).
 add_core_files( [
   'test.rb'
 ] ).
 # add_additional_files( [
 #   'README',
 #   'LICENSE',
 #   'AUTHORS',
 #   'Credits',
 #   'ChangeLog'
 # ] ).
 executable(
   :startup_rb_file => 'bin/Release.rb'
 )