# -*- mode: ruby -*-
# vi: set ft=ruby :

# Minimum required Vagrant version
Vagrant.require_version ">= 1.6.5"

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "mattiashem/syco_prep_centos6"
  config.vm.network "public_network", bridge: 'wlp3s0'

  # TODO, set owner? Need to be done after httpd is installed, owner: "apache", group: "apache"
  config.vm.synced_folder ".", "/var/syco-signer/"
  config.vm.synced_folder ".", "/vagrant/"
  config.vm.provision :shell, path: "./bin/vagrant-provision"
  config.vm.post_up_message = "Syco sandbox installed"
  config.ssh.username="vagrant"
  config.ssh.password="vagrant"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 8443

  config.vm.post_up_message = "syco-signer sandbox installed

Access with browser on http://127.0.0.1:8080"
end

