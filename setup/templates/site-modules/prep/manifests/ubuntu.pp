# Class: prep::Ubuntu
#
# This class will prep Debian and Ubuntu systems for Kubernetes
class prep::ubuntu (
  Array   $packages     = lookup('prep::ubuntu::packages_prep'),
  String  $pgp_key_source = lookup('prep::ubuntu.pgp_key_source'),
  String  $pgp_key_id     = lookup('prep::ubuntu.pgp_key_id'),
) {

  include apt
  include docker

  package { $packages:
    ensure => 'present'
  }

  apt::key { $pgp_key_id:
    ensure => present,
    server => $pgp_key_source,
  }

  exec {'apt update':
    command => '/usr/bin/apt update -y',
    require => Apt::Key[$pgp_key_id]
  }
}
