#!/usr/bin/python

import sys
import euca_qa

def debian_package_upgrade(host):
    ret = 0
    if config['memodict'].has_key('LOCAL_UPGRADE_REPO'):
        if host.dist == 'debian':
            host.run_command("echo deb %s squeeze main  >> /etc/apt/sources.list" % 
                             config['memodict']['LOCAL_UPGRADE_REPO'])
        else:
            host.run_command("echo deb %s lucid universe  >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_UPGRADE_REPO'])

    else:
        ### from eucalyptussoftware.com
        if config['bzr_branch'] == "2.0.0":
            ### TEMP FOR RELEASE 110210 - release
            ret |= host.run_command("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/debian/ squeeze main  >> /etc/apt/sources.list")

            ### nightly 2.0.0
            #               run_cmd("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/2.0.0/debian/ squeeze main  >> /etc/apt/sources.list");
        else: 
            ### nightly main
            ret |= host.run_command("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/debian/ squeeze main  >> /etc/apt/sources.list")

    ### set up Euca2ools REPO       020411
    if config['memodict'].has_key('LOCAL_EUCA2OOLS_UPGRADE_REPO'):
        if host.dist == 'debian':
            ret |= host.run_command("echo deb %s squeeze main >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])
	else:
            ret |= host.run_command("echo deb %s lucid universe >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])
	ret |= host.run_command("apt-get update")

        ret |= host.run_command("export DEBIAN_FRONTEND=noninteractive; apt-get install -y --force-yes -o Dpkg::Options::='--force-confnew' $( dpkg -l 'eucalyptus*' | grep 'ii' | awk '{print $2;}' | egrep 'cloud|cc|sc|walrus|broker|nc' )")
        ret |= host.run_command("export DEBIAN_FRONTEND=noninteractive; dpkg -l eucalyptus-cloud && apt-get install -y --force-yes eucalyptus-enterprise-vmwarebroker eucalyptus-enterprise-storage-san")

    return ret

def opensuse_package_upgrade(host):
    ret = host.run_command("zypper rr Eucalyptus")
 
    if config['memodict'].has_key('LOCAL_UPGRADE_REPO'):
        ret |= host.run_command("zypper ar --refresh %s Eucalyptus" % config['memodict']['LOCAL_UPGRADE_REPO'])
    else:
        if config['bzr_branch'] == "2.0.0":
            ### TEMP FOR RELEASE 110210 - release
            ret |= host.run_command("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/yum/opensuse Eucalyptus")

            # nightly - 2.0.0
            #  run_cmd("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/2.0.0/yum/opensuse Eucalyptus");
        else:
            # nightly - main
            ret |= host.run_command("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/yum/opensuse Eucalyptus")

    ### set up Euca2ools REPO       020411
    if config['memodict'].has_key('LOCAL_EUCA2OOLS_UPGRADE_REPO'):
        ret |= host.run_command("zypper rr Euca2ools")
        ret |= host.run_command("zypper ar --refresh %s Euca2ools" % 
                         config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])

    ret |= host.run_command("zypper --no-gpg-checks refresh Eucalyptus")
    ret |= host.run_command("zypper --no-gpg-checks refresh Euca2ools")
    ret |= host.run_command("zypper -n up -t package")

    return ret

def centos_package_upgrade(host):
    distro = 'centos'
    if host.dist == 'fedora':
        distro = 'fedora'

    ret = host.run_command("touch /etc/yum.repos.d/euca.repo")
    ret |= host.run_command("echo '[euca_upgrade]' >> /etc/yum.repos.d/euca.repo")
    ret |= host.run_command("echo 'name=Eucalyptus' >> /etc/yum.repos.d/euca.repo");

    if config['memodict'].has_key('LOCAL_UPGRADE_REPO'):
        print "Setting baseurl to %s" % config['memodict']['LOCAL_UPGRADE_REPO'];
        ret |= host.run_command("echo 'baseurl=%s' >> /etc/yum.repos.d/euca.repo" %
                                config['memodict']['LOCAL_UPGRADE_REPO'])
    else:
        if config['bzr_branch'] == "2.0.0":
            ### TEMP FOR RELEASE 110210 - release
            ret |= host.run_command("echo 'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/yum/%s/' >> /etc/yum.repos.d/euca.repo" % distro)
        else:
            # nightly - main
            ret |= host.run_command("echo 'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/yum/%s/' >> /etc/yum.repos.d/euca.repo" % distro)
    ret |= host.run_command("echo 'enabled=1' >> /etc/yum.repos.d/euca.repo")

    # Add extra repo for enterprise bits in 3.1
    if config['memodict'].has_key('EXTRA_UPGRADE_REPO'):
        ret = host.run_command("touch /etc/yum.repos.d/euca_extra.repo")
        ret |= host.run_command("echo '[euca_upgrade_extra]' >> /etc/yum.repos.d/euca_extra.repo")
        ret |= host.run_command("echo 'name=Eucalyptus' >> /etc/yum.repos.d/euca_extra.repo");
        print "Setting baseurl to %s" % config['memodict']['EXTRA_UPGRADE_REPO'];
        ret |= host.run_command("echo 'baseurl=%s' >> /etc/yum.repos.d/euca_extra.repo" %
                                config['memodict']['EXTRA_UPGRADE_REPO'])
        ret |= host.run_command("echo -e 'enabled=1\ngpgcheck=0' >> /etc/yum.repos.d/euca_extra.repo")

    if config['memodict'].has_key('LOCAL_EUCA2OOLS_UPGRADE_REPO'):
        ret |= host.run_command("echo '[euca2ools_upgrade]' >> /etc/yum.repos.d/euca2ools.repo")
        ret |= host.run_command("echo 'name=Euca2ools' >> /etc/yum.repos.d/euca2ools.repo")
        ret |= host.run_command("echo 'baseurl=%s' >> /etc/yum.repos.d/euca2ools.repo" % 
                         config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])
        ret |= host.run_command("echo -e 'enabled=1\ngpgcheck=0' >> /etc/yum.repos.d/euca2ools.repo")

    ret |= host.run_command("yum update -y --nogpgcheck");
    ret |= host.run_command("v=$( rpm -q --qf '%%{VERSION}' eucalyptus-cloud ); if [ ${v:0:3} == '3.1' ]; then yum install -y eucalyptus-enterprise-vmware-broker eucalyptus-enterprise-storage-san; fi")

    return ret

config = euca_qa.read_test_config()

ret = 0
for host in config['hosts']:
    if host.dist in ['centos', 'rhel', 'fedora']:
        ret |= centos_package_upgrade(host)
    elif host.dist in ['debian', 'ubuntu']:
        ret |= debian_package_upgrade(host)
    elif host.dist == 'opensuse':
        ret |= opensuses_package_upgrade(host)
    elif host.dist in ['vmware', 'windows']:
        print "[TEST REPORT] skipping %s system" % host.dist
        continue
    else:
       print "\n[TEST_REPORT]\tFAILED to find upgrade function for %s\n" % host.dist;

sys.exit(ret)
