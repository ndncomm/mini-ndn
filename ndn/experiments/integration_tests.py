# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015 The University of Memphis,
#                    Arizona Board of Regents,
#                    Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

from ndn.experiments.experiment import Experiment

from mininet.clean import sh

import os

class IntegrationTests(Experiment):

    def __init__(self, args):
        Experiment.__init__(self, args)

    def setup(self):
        print "Creating SSH keys"

        sh("mkdir -p /tmp/minindn")
        sh("rm -f /tmp/minindn/ssh_host_rsa_key")
        sh("ssh-keygen -q -t rsa -N '' -f /tmp/minindn/ssh_host_rsa_key")
        sh("rm -f /tmp/minindn/id_rsa")
        sh("ssh-keygen -q -t rsa -N '' -f /tmp/minindn/id_rsa")
        sh("cat /tmp/minindn/id_rsa.pub > /tmp/minindn/authorized_keys")

        sshd_cmd = ['/usr/sbin/sshd',
                    '-q',
                    '-o AuthorizedKeysFile=/tmp/minindn/authorized_keys',
                    '-o HostKey=/tmp/minindn/ssh_host_rsa_key',
                    '-o StrictModes=no']
        for host in self.net.hosts:
            # Run SSH daemon
            host.cmd(sshd_cmd)

            # Create a wrapper script for ssh that uses the generated key as default SSH identity
            host.cmd("mkdir -p ~/bin")
            homedir = host.cmd("echo -n ${HOME}")
            ssh_wrapper = homedir + '/bin/ssh'
            with open(ssh_wrapper, 'w') as f:
                f.writelines([
                    '#!/bin/sh\n',
                    'exec /usr/bin/ssh -f -i /tmp/minindn/id_rsa -o StrictHostKeyChecking=no "$@"\n'
                ])
            os.chmod(ssh_wrapper, 0755)
            host.cmd("export PATH=\"${HOME}/bin${PATH:+:}${PATH}\"")

            # Copy nfd configuration into default configuration location
            host.cmd("cp %s %s" % (host.nfd.confFile, "/usr/local/etc/ndn/nfd.conf"))

            if host.name == "a":
                sh("cp -r integration-tests /tmp/a")

    def run(self):
        for host in self.net.hosts:
            if host.name == "a":
                host.cmd("cd integration-tests")

                tests = [
                    #"test_linkfail",
                    #"test_hub_discovery",
                    #"test_interest_loop",
                    #"test_interest_aggregation",
                    #"test_localhost_scope",
                    #"test_multicast_strategy",
                    #"test_multicast",
                    #"test_tcp_udp_tunnel",
                    #"test_localhop",
                    "test_unixface",
                    "test_ndnpeekpoke",
                    "test_route_expiration",
                    #"test_nfdc",
                    "test_ndnping",
                    "test_cs_freshness",
                    "test_nrd",
                    "test_fib_matching",
                    #"test_remote_register",
                    "test_ndntraffic"
                ]

                for test in tests:
                    host.cmd("./run_tests.py %s" % test, verbose=True)

Experiment.register("integration-tests", IntegrationTests)
