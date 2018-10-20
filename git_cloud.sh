#!/usr/bin/env bash

eval 'set +o history' 2>/dev/null || setopt HIST_IGNORE_SPACE 2>/dev/null
 touch ~/.gitcookies
 chmod 0600 ~/.gitcookies

 git config --global http.cookiefile ~/.gitcookies

 tr , \\t <<\__END__ >>~/.gitcookies
source.developers.google.com,FALSE,/,TRUE,2147483647,o,git-hlvua.pro.gmail.com=1/EF6S8s5WI4tyIBU1gZ9XPnoTrya5dp7SoRk_21k9Kyg
__END__
eval 'set -o history' 2>/dev/null || unsetopt HIST_IGNORE_SPACE 2>/dev/null
