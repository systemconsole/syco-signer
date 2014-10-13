# -*- mode: ruby -*-
# vi: set ft=ruby :

# Minimum required Vagrant version
Vagrant.require_version ">= 1.6.5"

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Renter is always placed under /var/renter
  # This is done from vagrant-mount, because user and group are not created yet.
  config.vm.synced_folder ".", "/var/www/syco-signer/", owner: "apache", group: "apache"

  # Every Vagrant virtual environment requires a box to build off.
  # INFO: https://vagrantcloud.com/hansode/boxes/centos-6.6-x86_64
  config.vm.box = "hansode/centos-6.6-x86_64"

  # Install renter on the box
  config.vm.provision :shell, path: "./bin/vagrant-provision"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 8443

  # Forward port 80/443 on host to 8080/8443 on vagrant.
  # Only working on os x
config.trigger.after [:provision, :up, :reload] do
      system('
sudo pfctl -e;
echo "
rdr pass on lo0 inet proto tcp from any to 127.0.0.1 port 80 -> 127.0.0.1 port 8080
rdr pass on lo0 inet proto tcp from any to 127.0.0.1 port 443 -> 127.0.0.1 port 8443
" | sudo pfctl -f - > /dev/null 2>&1;

echo "==> Fowarding Ports: 80 -> 8080, 443 -> 8443"')
  end

  config.trigger.after [:halt, :destroy, :suspend] do
    system("sudo pfctl -f /etc/pf.conf > /dev/null 2>&1; echo '==> Removing Port Forwarding'")
  end

  config.vm.post_up_message = "Renter sandbox installed

Add to /etc/hosts
# Renter Sandbox
127.0.0.1 www-sb.renter.se
127.0.0.1 api-sb.renter.se"
end

