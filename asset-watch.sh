#!/bin/bash
coffee -o public/js -cw assets/coffee &
sass --watch assets/scss:public/css
kill %1