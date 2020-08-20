# Deploy Kubernetes to Primaries and Runners
plan deploy_k8s::deploy () {

    # Prep the hosts; install Puppet Agent and Facter
    apply_prep(['application_servers'])

    # Prep the hosts; configure the sysctl 
    apply('application_servers', _run_as => root) {
        # Ensures the conntrack count value is set to 0
        sysctl { 'net.netfilter.nf_conntrack_count':
            ensure  => present,
            value   => '0',
            comment => 'Required for Kubernetes',
        }

        sysctl {'vm.max_map_count':
            ensure     => present,
            value      => $vm_max_map_count,
            comment    => 'Required for various Kubernetes services',
            persistent => true
        }

        sysctl {'fs.file-max':
            ensure     => present,
            value      => $fs_file_max,
            comment    => 'Required for various Kubernetes services',
            persistent => true
        }
    }

    # Deploy the Kubernetes Controller
    apply('k8s-primary', _run_as => root) {
        # Use the Ubuntu Hiera file and provision the Kubernetes controller.
        class {'kubernetes':
            controller => true,
            require    => Sysctl['net.netfilter.nf_conntrack_count']
        }
    }

    # Deploy the Kubernetes Worker or workers
    apply('k8s-nodes', _run_as => root) {
        # Use the Ubuntu Hiera file and provision the Kubernetes workers.
        class {'kubernetes':
            worker  => true,
            require => Sysctl['net.netfilter.nf_conntrack_count']
        }
    }
}
