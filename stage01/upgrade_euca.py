#!/usr/bin/python

import sys
import euca_qa

# Hard-coded for now
REPO_API="http://192.168.51.243:5000/genrepo"

def debian_package_upgrade(host):
    ret = 0
    if config['memodict'].has_key('LOCAL_UPGRADE_REPO'):
        if host.dist == 'debian':
            host.run_cmd("echo deb %s squeeze main  >> /etc/apt/sources.list" % 
                             config['memodict']['LOCAL_UPGRADE_REPO'])
        else:
            host.run_cmd("echo deb %s lucid main universe  >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_UPGRADE_REPO'])

    if config['memodict'].has_key('LOCAL_EUCA2OOLS_UPGRADE_REPO'):
        if host.dist == 'debian':
            host.run_cmd("echo deb %s squeeze main >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])
	else:
            host.run_cmd("echo deb %s lucid main universe >> /etc/apt/sources.list" %
                             config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'])
	host.run_cmd("apt-get update")

        # XXX - Removed -o Dpkg::Options::='--force-confnew' here; old upgrades (pre-3.1) need that, though
        ret |= host.run_cmd("export DEBIAN_FRONTEND=noninteractive; apt-get install -y --force-yes $( dpkg -l 'eucalyptus*' | grep 'ii' | awk '{print $2;}' | egrep 'cloud|cc|sc|walrus|broker|nc' )")
        ret |= host.run_cmd("export DEBIAN_FRONTEND=noninteractive; dpkg -l eucalyptus-cloud && apt-get install -y --force-yes eucalyptus-enterprise-vmwarebroker eucalyptus-enterprise-storage-san eucalyptus-cloud")

    return ret

def centos_package_upgrade(host):
    repofile = "/etc/yum.repos.d/euca.repo"
    host.run_cmd("touch " + repofile)
    host.run_cmd("echo '[euca_upgrade]' >> " + repofile)
    host.run_cmd("echo 'name=Eucalyptus' >> " + repofile);

    # change a git url to something acceptable to genrepo service
    git_internal_url = None
    git_euca_url = config['git_url'].split('/', 2)[-1].replace("/", ":")
    if git_euca_url.endswith(':internal'):
        git_internal_url = git_euca_url
        git_euca_url = git_internal_url.replace(':internal', ':eucalyptus')

    if config['memodict'].has_key('LOCAL_UPGRADE_REPO'):
        print "Setting baseurl to %s" % config['memodict']['LOCAL_UPGRADE_REPO'];
        host.run_cmd("echo 'baseurl=%s' >> %s" %
                                (config['memodict']['LOCAL_UPGRADE_REPO'], repofile))
    else:
        mirrorurl = "%s?url=%s&ref=%s&distro=%s&releasever=$releasever&arch=$basearch" % (REPO_API, git_euca_url, config['git_branch'], host.dist)
        print "Setting mirrorurl to %s" % mirrorurl
        host.run_cmd("echo 'mirrorlist=%s' >> %s" % (mirrorurl, repofile))
    host.run_cmd("echo 'enabled=1' >> " + repofile)

    # Add extra repo for enterprise bits in 3.1
    if git_internal_url is not None or config['memodict'].has_key('ENT_UPGRADE_REPO'):
        repofile = "/etc/yum.repos.d/euca_enterprise.repo"
        host.run_cmd("touch " + repofile)
        host.run_cmd("echo '[euca_upgrade_ent]' >> " + repofile)
        host.run_cmd("echo 'name=Eucalyptus Enterprise' >> " + repofile);
        if config['memodict'].has_key('ENT_UPGRADE_REPO'):
            host.run_cmd("echo 'baseurl=%s' >> %s" %
                             (config['memodict']['ENT_UPGRADE_REPO'], repofile))
        else:
            host.run_cmd("echo 'mirrorlist=%s?url=%s&ref=%s&distro=%s&releasever=$releasever&arch=$basearch' >> %s" %
                             (REPO_API, git_internal_url, config['git_branch'], host.dist, repofile) )
        host.run_cmd("echo -e 'enabled=1\ngpgcheck=0' >> " + repofile)

    if config['memodict'].has_key('LOCAL_EUCA2OOLS_UPGRADE_REPO'):
        repofile = "/etc/yum.repos.d/euca2ools.repo"
        host.run_cmd("echo '[euca2ools_upgrade]' >> " + repofile)
        host.run_cmd("echo 'name=Euca2ools' >> " + repofile)
        host.run_cmd("echo 'baseurl=%s' >> %s" % 
                         (config['memodict']['LOCAL_EUCA2OOLS_UPGRADE_REPO'], repofile) )
        host.run_cmd("echo -e 'enabled=1\ngpgcheck=0' >> " + repofile)

    host.run_cmd("yum update -y --nogpgcheck");
    if host.has_role('clc'):
        host.run_cmd("v=$( rpm -q --qf '%{VERSION}' eucalyptus ); if [ ${v:0:3} == '3.1' ]; then yum groupinstall -y eucalyptus-cloud-controller --nogpgcheck; fi")

    return ret

config = euca_qa.read_test_config()

ret = 0
for host in config['hosts']:
    if host.dist in ['centos', 'rhel', 'fedora']:
        ret |= centos_package_upgrade(host)
    elif host.dist in ['debian', 'ubuntu']:
        ret |= debian_package_upgrade(host)
    elif host.dist in ['vmware', 'windows']:
        print "[TEST REPORT] skipping %s system" % host.dist
        continue
    else:
       print "\n[TEST_REPORT]\tFAILED to find upgrade function for %s\n" % host.dist;

sys.exit(ret)
