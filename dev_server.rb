#!/usr/bin/env ruby
args=ARGV.clone
args+='-a $IP -p $PORT' if ENV['IP'] and ENV['PORT']
exec "dev_appserver.py  #{args.join(' ')} --disable_static_caching --enable_console --use_sqlite ."