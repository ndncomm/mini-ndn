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

class IntegrationTests(Experiment):

    def __init__(self, args):
        Experiment.__init__(self, args)

    def setup(self):
        print "Creating SSH keys"

        sh("rm -rf /tmp/ssh")
        sh("mkdir /tmp/ssh")
        sh("ssh-keygen -t rsa -P '' -f /tmp/ssh/id_rsa")
        sh("cat /tmp/ssh/id_rsa.pub >> /tmp/ssh/authorized_keys")

        cmd = "/usr/sbin/sshd"
        opts = "-D -o AuthorizedKeysFile=/tmp/ssh/authorized_keys -o StrictModes=no"

        for host in self.net.hosts:
            # Run SSH daemon
            host.cmd(cmd + " " + opts + "&")

            # Use generated private key as default SSH identity
            host.cmd("alias ssh=\"ssh -i /tmp/ssh/id_rsa\"")

    def run(self):
        pass

Experiment.register("integration-tests", IntegrationTests)
