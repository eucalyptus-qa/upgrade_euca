#!/usr/bin/perl

# select(STDERR);$|=1;select(STDOUT);$|=1;
my @ips = ();

sub run_cmd{
    my $remote_cmd = shift;
    my $ip;
    print "running on all hosts: $remote_cmd\n";
    foreach $ip (@ips) {
       my $cmd = "ssh -o StrictHostKeyChecking=no root\@$ip \"$remote_cmd\"";
       print "Running $cmd\n";
       my $result = `$cmd`;
       print "Result:\n$result\n";
    }    
}

sub read_input_file{
        open( LIST, "../input/2b_tested.lst" ) or return 1;
        my $is_memo;
        my $memo = "";                                                                                                                                                       
        
        my $line;
        while( $line = <LIST> ){
                chomp($line);
                if( $is_memo ){
                        if( $line ne "END_MEMO" ){
                                $memo .= $line . "\n";
                        };
                };
                if( $line =~ /^(.+)\t(.+)\t(.+)\t(\d+)\t(.+)\t\[(.+)\]/ ){
                        ### below aren't used for now
                        if ($2 =~ /vmware/i) {
                            next;
                        }
                        push(@ips, $1);
                        $ENV{'QA_DISTRO'} = $2;
                        $ENV{'QA_DISTRO_VER'} = $3;
                        $ENV{'QA_ARCH'} = $4;
                        $ENV{'QA_SOURCE'} = $5;
                }elsif( $line =~ /^BZR_BRANCH\t(.+)/ ){
                        my $temp = $1;
                        chomp($temp);
                        $temp =~ s/\r//g;
                        if( $temp =~ /eucalyptus\/(.+)/ ){
                                $ENV{'QA_BZR_DIR'} = $1; 
                        };
                }elsif( $line =~ /^MEMO/ ){
                        $is_memo = 1;
                }elsif( $line =~ /^END_MEMO/ ){
                        $is_memo = 0;
                };              
        };
        close(LIST);
        
        $ENV{'QA_MEMO'} = $memo;
        
        return 0;
};      

sub does_It_Have{
        my ($string, $target) = @_;
        if( $string =~ /$target/ ){
                return 1;
        };
        return 0;
};

sub is_local_euca2ools_upgrade_repo_from_memo{
       $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} = "";
       if( $ENV{'QA_MEMO'} =~ /LOCAL_EUCA2OOLS_UPGRADE_REPO=(.+)\n/ ){
               my $extra = $1;
               $extra =~ s/\r//g;
               print "FOUND in MEMO\n";
               print "LOCAL_EUCA2OOLS_UPGRADE_REPO=$extra\n";
               $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} = $extra;
               return 1;
       };
       return 0;
};

sub is_local_upgrade_repo_from_memo{
       $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} = "";
       if( $ENV{'QA_MEMO'} =~ /LOCAL_UPGRADE_REPO=(.+)\n/ ){
               my $extra = $1;                 
               $extra =~ s/\r//g;              
               print "FOUND in MEMO\n";        
               print "LOCAL_UPGRADE_REPO=$extra\n";
               $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} = $extra;
               return 1;                       
       };   
       return 0;                               
};          



sub ubuntu_package_install{
    return debian_package_install();
}


sub debian_package_install{

       my $distro = $ENV{'QA_DISTRO'};
       my $source = $ENV{'QA_SOURCE'};
       my $roll = $ENV{'QA_ROLL'};

       my $bzr_dir = $ENV{'QA_BZR_DIR'};
       my $pkg_branch = "1.6";

       ### set up REPO
       if( $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} ne "" ){
               my $local_repo = $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'};
	       if( $distro eq "debian") {
                   run_cmd("echo deb $local_repo squeeze main  >> /etc/apt/sources.list");
               } else {
                   run_cmd("echo deb $local_repo lucid universe  >> /etc/apt/sources.list");
               }

       }else{
               ### from eucalyptussoftware.com
               if( $bzr_dir eq "2.0.0" ){
                       ### TEMP FOR RELEASE 110210 - release
                       run_cmd("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/debian/ squeeze main  >> /etc/apt/sources.list");

                       ### nightly 2.0.0
       #               run_cmd("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/2.0.0/debian/ squeeze main  >> /etc/apt/sources.list");
               }else{
                       ### nightly main
                       run_cmd("echo deb http://eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/debian/ squeeze main  >> /etc/apt/sources.list");
               };
       };

       ### set up Euca2ools REPO       020411
       if( $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} ne "" ){
               my $local_euca2ools_repo = $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'};
	       if( $distro eq "debian") {
		   run_cmd("echo deb $local_euca2ools_repo squeeze main >> /etc/apt/sources.list");
	       } else {
		   run_cmd("echo deb $local_euca2ools_repo lucid universe >> /etc/apt/sources.list");
	       }
	       run_cmd("apt-get update");
       };


       # run_cmd("export DEBIAN_FRONTEND=noninteractive; apt-get upgrade -y --force-yes");
       run_cmd("export DEBIAN_FRONTEND=noninteractive; apt-get install -y --force-yes -o Dpkg::Options::='--force-confnew' \\\$( dpkg -l 'eucalyptus*' \| grep 'ii' \| awk '{print \\\$2;}' \| egrep 'cloud|cc|sc|walrus|broker|nc' )");

       return 0;
};


sub opensuse_package_install{

       my $distro = $ENV{'QA_DISTRO'};
       my $source = $ENV{'QA_SOURCE'};
       my $roll = $ENV{'QA_ROLL'};
       my $bzr_dir = $ENV{'QA_BZR_DIR'};

       run_cmd("zypper rr Eucalyptus");
 
       ### set up REPO
       if( $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} ne "" ){
               my $local_repo = $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'};
               run_cmd("zypper ar --refresh $local_repo Eucalyptus");
       }else{
               if( $bzr_dir eq "2.0.0" ){
                       ### TEMP FOR RELEASE 110210 - release
                       run_cmd("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/yum/opensuse Eucalyptus");

                       # nightly - 2.0.0
       #               run_cmd("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/2.0.0/yum/opensuse Eucalyptus");
               }else{
                       # nightly - main
                       run_cmd("zypper ar --refresh http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/yum/opensuse Eucalyptus");
               };
       };

       ### set up Euca2ools REPO       020411
       if( $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} ne "" ){
               my $local_euca2ools_repo = $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'};
               run_cmd("zypper rr Euca2ools");
               run_cmd("zypper ar --refresh $local_euca2ools_repo Euca2ools");
       };


       run_cmd("zypper --no-gpg-checks refresh Eucalyptus");
       run_cmd("zypper --no-gpg-checks refresh Euca2ools");

       my $pkgname = "eucalyptus";

       run_cmd("zypper -n up -t package");

       return 0;
};

sub centos_package_install{

       my $distro = $ENV{'QA_DISTRO'};
       my $arch = $ENV{'QA_ARCH'};
       my $source = $ENV{'QA_SOURCE'};
       my $roll = $ENV{'QA_ROLL'};
       my $bzr_dir = $ENV{'QA_BZR_DIR'};

       run_cmd("touch /etc/yum.repos.d/euca.repo");
       run_cmd("echo \'[euca_upgrade]\' >> /etc/yum.repos.d/euca.repo");
       run_cmd("echo \'name=Eucalyptus\' >> /etc/yum.repos.d/euca.repo");

       ### set up REPO
       if( $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} ne "" ){
               my $local_repo = $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'};
               print "Setting baseurl to $local_repo\n";
               run_cmd("echo \'baseurl=" . $local_repo ."\' >> /etc/yum.repos.d/euca.repo");
       }else{
               if( $ENV{'BZR_DIR'} eq "2.0.0" ){
                       ### TEMP FOR RELEASE 110210 - release
                       run_cmd("echo \'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/yum/centos/\' >> /etc/yum.repos.d/euca.repo");
               }else{
                       # nightly - main
                       run_cmd("echo \'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/yum/centos/\' >> /etc/yum.repos.d/euca.repo");
               };
       };
       run_cmd("echo \'enabled=1\' >> /etc/yum.repos.d/euca.repo");

       ### Temp. Sol. add euca2ools repo 020411


       if( $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} ne "" ){
               my $local_euca2ools_repo = $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'};
               run_cmd("echo \'[euca2ools_upgrade]\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'name=Euca2ools\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'baseurl=" . $local_euca2ools_repo ."\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'enabled=1\' >> /etc/yum.repos.d/euca2ools.repo");
       };

       run_cmd("python2.4 /usr/bin/yum update -y --nogpgcheck");

       return 0;
};

sub fedora_package_install{

       my $distro = $ENV{'QA_DISTRO'};
       my $arch = $ENV{'QA_ARCH'};
       my $source = $ENV{'QA_SOURCE'};
       my $roll = $ENV{'QA_ROLL'};
       my $bzr_dir = $ENV{'QA_BZR_DIR'};

       run_cmd("touch /etc/yum.repos.d/euca.repo");
       run_cmd("echo \'[euca_upgrade]\' >> /etc/yum.repos.d/euca.repo");
       run_cmd("echo \'name=Eucalyptus\' >> /etc/yum.repos.d/euca.repo");

       ### set up REPO
       if( $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'} ne "" ){
               my $local_repo = $ENV{'QA_MEMO_LOCAL_UPGRADE_REPO'};
               run_cmd("echo \'baseurl=" . $local_repo . "\' >> /etc/yum.repos.d/euca.repo");
       }else{
               if( $bzr_dir eq "2.0.0" ){
                       ### TEMP FOR RELEASE - release
                       run_cmd("echo \'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/2.0.1/yum/fedora/\' >> /etc/yum.repos.d/euca.repo");

                       # nightly - 2.0.0
       #               run_cmd("echo \'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/2.0.0/yum/fedora/\' >> /etc/yum.repos.d/euca.repo");
               }else{
                       # nightly - main
                       run_cmd("echo \'baseurl=http://www.eucalyptussoftware.com/downloads/repo/eucalyptus/nightly/main/yum/fedora/\' >> /etc/yum.repos.d/euca.repo");
               };
       };
       run_cmd("echo \'enabled=1\' >> /etc/yum.repos.d/euca.repo");

       ### set up Euca2ools REPO       020411
       if( $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'} ne "" ){
               my $local_euca2ools_repo = $ENV{'QA_MEMO_LOCAL_EUCA2OOLS_UPGRADE_REPO'};
               run_cmd("echo \'[euca2ools_upgrade]\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'name=Euca2ools\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'baseurl=" . $local_euca2ools_repo . "\' >> /etc/yum.repos.d/euca2ools.repo");
               run_cmd("echo \'enabled=1\' >> /etc/yum.repos.d/euca2ools.repo");
       };

       run_cmd("yum update -y --nogpgcheck");

       return 0;
};

sub rhel_package_install{
       return centos_package_install();
};


read_input_file();
my $distro = $ENV{'QA_DISTRO'};

$ENV{'EUCALYPTUS'} = "";

is_local_upgrade_repo_from_memo();
is_local_euca2ools_upgrade_repo_from_memo();

$distro =~ tr/[A-Z]/[a-z]/;
if ($distro =~ /(centos|rhel|debian|opensuse|ubuntu|fedora)/) {
       print "going to run $distro" . "_package_install\n";
       my $return_code = ($distro . '_package_install')->();
       exit $return_code;
} else {
       print "\n[TEST_REPORT]\tFAILED to find upgrade function for $distro\n";
}
exit 1;

