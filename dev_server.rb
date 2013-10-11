#!/usr/bin/env ruby
args=ARGV.clone
args<<'-a $IP -p $PORT -c' if ENV['IP'] and ENV['PORT']#cloud9 datastore should be cleared on each launch
exec "dev_appserver.py  #{args.join(' ')} ."