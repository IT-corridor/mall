# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8776, host: 8001
  config.vm.network "forwarded_port", guest: 8777, host: 8002
  config.vm.synced_folder "data/", "/vagrant_data"
  config.vm.provision "shell", path: "bootstrap/bootstrap.sh"
  #config.vm.provision "shell", path: "start_db.sh"
  config.vm.provision "shell", path: "bootstrap/start.sh", run: "always"
end