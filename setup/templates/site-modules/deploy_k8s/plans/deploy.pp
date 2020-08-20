# Deploy Kubernetes to Primaries and Runners
plan deploy_k8s::deploy (
    Integer     $vm_max_map_count   = lookup('deploy_k8s::deploy.vm_max_map_count'),
    Integer     $fs_file_max        = lookup('deploy_k8s::deploy.fs_file_max'),
    String      $docker_daemon      = lookup('prep::ubuntu::docker_daemon_json'),
) {

    # Prep the hosts; install Puppet Agent and Facter
    apply_prep(['application_servers'])

    # Prep the hosts; configure the sysctl values
    apply('application_servers', _run_as => root) {
        # Sets the vm.max_map_count value
        sysctl {'vm.max_map_count':
            ensure  => present,
            value   => $vm_max_map_count,
            comment => 'Required for various Kubernetes services',
            persist => true
        }

        # Sets the fs.file-max value
        sysctl {'fs.file-max':
            ensure  => present,
            value   => $fs_file_max,
            comment => 'Required for various Kubernetes services',
            persist => true
        }

        case $facts['os']['name'] {
            'RedHat', 'CentOS':     { include prep::redhat  }
            /^(Debian|Ubuntu)$/:    { include prep::ubuntu  }
            default:                { include prep::generic }
        }
    }

    # Update the Docker Daemon
    apply('application_servers', _run_as => root) {
        file { '/etc/docker/daemon.json':
            content => $docker_daemon,
            notify  => Exec['daemon-reload']
        }

        exec { 'daemon-reload':
            command     => '/bin/systemctl daemon-reload',
            refreshonly => true,
        }
    }

    # Deploy the Kubernetes Controller
    apply('k8s-primary', _run_as => root) {
        # Use the Ubuntu Hiera file and provision the Kubernetes controller.
        class {'kubernetes':
            controller => true,
        }
    }

    # Deploy the Kubernetes Worker or workers
    apply('k8s-nodes', _run_as => root) {
        # Use the Ubuntu Hiera file and provision the Kubernetes workers.
        class {'kubernetes':
            worker  => true,
        }
    }

    # Validate functionality of the Kubernetes Cluster
    apply('k8s-primary', _run_as => root) {
        exec {'kubectl-verify':
            command => '/usr/bin/kubectl get nodes --kubeconfig /etc/kubernetes/admin.conf'
        }
    }

}
