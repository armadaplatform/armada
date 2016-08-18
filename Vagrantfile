def armada_vagrantfile(args={})
    microservice_name = args[:microservice_name]
    armada_run_args = args[:armada_run_args]
    origin_dockyard_address = args[:origin_dockyard_address]
    configs_dir = args[:configs_dir]
    secret_configs_repository = args[:secret_configs_repository]

    vagrantfile_api_version = "2"

    Vagrant.configure(vagrantfile_api_version) do |config|

        config.vm.box = "ubuntu/xenial64"
        # Fix for slow (~5s) DNS resolving.
        config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        end

        # Port forwarding.
        config.vm.network "public_network", :adapter => 2

        # Mapping directories.
        config.vm.synced_folder "..", "/projects"

        config.vm.provision "shell", inline: <<SCRIPT
            apt-get -y install docker.io=1.10.3-0ubuntu6
            sudo usermod -aG docker ubuntu
            /projects/armada/install/install.sh ubuntu16
            docker rm -f `docker ps | grep armada | cut -f 1 -d ' '`
            rm /var/run/armada.pid
            sudo echo default_interface=enp0s8 > /etc/default/armada
            sudo systemctl restart armada.service
            sudo chmod 777 /etc/opt
SCRIPT
        if origin_dockyard_address then
            if origin_dockyard_address.index('http://') == 0 then
                http_origin_dockyard_address = origin_dockyard_address
            else
                http_origin_dockyard_address = 'http://' + origin_dockyard_address
            end
            config.vm.provision "shell", inline: <<SCRIPT
                dockyard_port=55000
                [[ -n $(curl -s localhost:8900/list?microservice_name=origin-dockyard-proxy | grep microservice_id) ]] && proxy_started=true || proxy_started=false
                while [[ "$proxy_started" != "true" && $dockyard_port -lt 55010 ]]
                do
                    armada run armada-bind -r origin-dockyard-proxy -e "SERVICE_ADDRESS=#{http_origin_dockyard_address}" -p ${dockyard_port}:80
                    status=$?
                    sleep 2
                    if [ $status -eq 0 ]; then
                        proxy_started=true
                        armada dockyard set origin localhost:$dockyard_port
                    else
                        dockyard_port=$((dockyard_port + 1))
                    fi
                done
SCRIPT
        end

        if microservice_name then
            if configs_dir then
                config.vm.provision "shell", inline: <<SCRIPT
                    if [ -h /etc/opt/#{microservice_name}-config ]; then
                        rm -f /etc/opt/#{microservice_name}-config
                    elif [ -e /etc/opt/#{microservice_name}-config ]; then
                        echo "WARNING: /etc/opt/#{microservice_name}-config exists but it is not a symbolic link."
                    fi
                    ln -s /opt/#{microservice_name}/#{configs_dir} /etc/opt/#{microservice_name}-config
SCRIPT
            end

            if secret_configs_repository then
                if not Dir.exists?('config-secret') then
                    `git clone #{secret_configs_repository} config-secret`
                end
                config.vm.provision "shell", inline: <<SCRIPT
                    if [ -h /etc/opt/#{microservice_name}-config-secret ]; then
                        rm -f /etc/opt/#{microservice_name}-config-secret
                    elif [ -e /etc/opt/#{microservice_name}-config-secret ]; then
                        echo "WARNING: /etc/opt/#{microservice_name}-config-secret exists but it is not a symbolic link."
                    fi
                    ln -s /opt/#{microservice_name}/config-secret /etc/opt/#{microservice_name}-config-secret
SCRIPT
            end

            config.vm.synced_folder "./", "/opt/#{microservice_name}"

            config.vm.provision "shell", inline: <<SCRIPT
                sudo -u ubuntu echo export MICROSERVICE_NAME='#{microservice_name}' >> /home/ubuntu/.bashrc
                MICROSERVICE_NAME='#{microservice_name}' armada run #{armada_run_args} | cat
SCRIPT
        end
    end
end


armada_vagrantfile :microservice_name => 'armada-src'

Vagrant.configure("2") do |config|
    config.vm.provision "shell", inline: <<SCRIPT
        chmod +x /opt/armada-src/armada_command/armada_dev/*
        cp /opt/armada-src/armada_command/armada_dev/* /usr/local/bin/
        sudo -u ubuntu echo export MICROSERVICE_NAME='armada' >> /home/ubuntu/.bashrc
        sudo -u ubuntu echo export ARMADA_AUTORELOAD='true' >> /home/ubuntu/.bashrc
        sed -i "s#'/opt/armada'#'/opt/armada-src'#" /usr/local/bin/armada
SCRIPT
end
