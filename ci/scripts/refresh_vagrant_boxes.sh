#!/usr/bin/env bash


printf 'Checking for available updates for installed vagrant boxes...\n'
vagrant box outdated --force --global

boxes=$(vagrant box list | cut -d ' ' -f1)

for box in $boxes
do
    printf 'Updating vagrant box: %s\n' "$box"
    vagrant box update --box "${box}"
done

printf 'Removing old version of vagrant boxes...\n'
vagrant box prune
