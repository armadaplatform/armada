# Workflow for Armada development:
# 1. $ vagrant up
# 2. $ vagrant ssh
# 3. Make changes in armada source code on your harddrive in directory that contains this Vagrantfile.
#      It is in sync with /opt/armada-src in Vagrant.
# 4. $ build-armada
# 5. $ restart-armada
# 6. Test changes.
# 7. $ armada push armada -d [dockyard]

require 'open-uri'
armada_vagrantfile_path = File.join(Dir.tmpdir, 'ArmadaVagrantfile.rb')
IO.write(armada_vagrantfile_path, open('http://vagrant.armada.sh/ArmadaVagrantfile.rb').read)
load armada_vagrantfile_path

armada_vagrantfile :microservice_name => 'armada-src'

Vagrant.configure("2") do |config|
    config.vm.provision "shell", inline: <<SCRIPT
        chmod +x /opt/armada-src/armada_command/armada_dev/*
        cp /opt/armada-src/armada_command/armada_dev/* /usr/local/bin/
        sudo -u vagrant echo export MICROSERVICE_NAME='armada' >> /home/vagrant/.bashrc
        sed -i "s#'/opt/armada'#'/opt/armada-src'#" /usr/local/bin/armada
SCRIPT
end
