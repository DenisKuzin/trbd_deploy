from fabric.api import task, run, put, cd, env
import os

env.hosts = ['root@192.168.0.101']

def put_dependency(dependency_path):
    u'''
    Transfer dependency files to remote host
    '''
    remote_path = os.path.join('trbd/dependency', dependency_path)
    if run('test -d %s' % remote_path, quiet=True).failed:
        run('mkdir -p %s' % os.path.dirname(remote_path))
        put(os.path.join('dependency', dependency_path), os.path.dirname(remote_path))

def install_dependency(dependency_path):
    u'''
    Install dependency on remote host
    '''
    put_dependency(dependency_path)
    with cd(os.path.join('trbd/dependency', dependency_path)):
        run('yum -y -q localinstall *.rpm')

@task
def scp():
    install_dependency('scp')

@task
def emacs():
    install_dependency('emacs')
    run('ln -s /usr/bin/emacs /usr/bin/e')

@task
def java():
    install_dependency('java')

@task
def tomcat6():
    install_dependency('tomcat6')
    run('chkconfig --level 2345 tomcat6 on')
    run('iptables -t filter -I INPUT 5 -p tcp --dport 8080 -j ACCEPT')
    run('service iptables save')

@task
def tomcat8():
    put_dependency('tomcat8')
    with cd('trbd/dependency/tomcat8'):
        run('tar -xf *.tar.gz -C /opt')
    with cd('/opt'):
        run('ln -s apache-tomcat-* tomcat')
    run('cp trbd/dependency/tomcat8/tomcat /etc/rc.d/init.d')
    with cd('/etc/rc.d/init.d'):
        run('chmod 755 tomcat')
        run('chkconfig --add tomcat')
        run('chkconfig --level 2345 tomcat on')
    run('iptables -t filter -I INPUT 5 -p tcp --dport 8080 -j ACCEPT')
    run('service iptables save')
    install_dependency('tomcatnative')

@task
def solr():
    put_dependency('solr')
    with cd('trbd/dependency/solr'):
        run('tar -xf solr-*.tgz -C /opt')
    with cd('/opt'):
        run('ln -s solr-* solr')

@task
def informix_csdk():
    install_dependency('bc')
    run('mkdir /opt/IBM')
    run('useradd -d /opt/IBM/informix informix')
    put_dependency('informix')
    run('mkdir /media/cdrom')
    run('mount -o loop trbd/dependency/informix/IDS1150LIN64.ISO /media/cdrom')
    with cd('/media/cdrom'):
        run('./ids_install -options "/root/trbd/dependency/informix/client.properties" -silent')

@task
def informix_server():
    install_dependency('bc')
    install_dependency('libncurses')
    run('mkdir /opt/IBM')
    run('useradd -d /opt/IBM/informix informix')
    put_dependency('informix')
    run('mkdir /media/cdrom')
    run('mount -o loop trbd/dependency/informix/IDS1150LIN64.ISO /media/cdrom')
    with cd('/media/cdrom'):
        run('./ids_install -options "/root/trbd/dependency/informix/server.properties" -silent')
