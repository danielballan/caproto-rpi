Caproto IOCs for Raspberry Pi
=============================

Headless RPi Setup
------------------

This documentation builds on 
`official docs <https://www.raspberrypi.org/documentation/configuration/wireless/headless.md>`_
for installing an operating system and getting your RPi on a password-protected
WiFi network without using a monitor or a keyboard. From there, we can
configure it over SSH.

* Download Raspbian Stretch Lite image (no desktop). See
  `Rpi downloads page <https://www.raspberrypi.org/downloads/raspbian/>`_.  
* Use `Etcher <https://etcher.io/>`_ to "flash" the SD card with this image.
* Mount the boot partition of the SD card.
* To enable ssh, create an empty file named ``ssh`` in the root of the boot
  partition.
* Add a file name ``wpa_supplicant.conf`` to that same directory with contents
  like:

  .. code-block:: ini

     country=GB
     ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
     update_config=1
     network={
         ssid="YOUR_WIFI_NETWORK_NAME"
         psk="PASSWORD_IN_PLAIN_TEXT"
     }

  For more details, see
  `official docs <https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md>`_.
* Unmount and eject the SD card. Load it into the RPi and plug in the RPi. The
  RPi should automatically boot and join the WiFi network with the hostname
  ``raspberrypi``.
* Copy ssh key(s). We use an option to avoid adding the host key to
  ``~/.ssh/known_hosts`` because we are about to change the hostname. Enter
  ``yes`` and the default password, ``raspberry``, when prompted.

  .. code-block:: bash

     ssh-copy-id -o "UserKnownHostsFile /dev/null" pi@raspberrypi
     ssh -o "UserKnownHostsFile /dev/null" pi@raspberrypi

* Install a proper editor (e.g. ``sudo apt install vim``).
* Set a unique hostname in ``/etc/hostname`` and last line of ``/etc/hosts``,
  such as ``pizero5``.
* Reboot: ``sudo reboot now``.
* After ~20 seconds, verify that you can login: ``ssh pi@NEW_HOSTNAME``. This
  time, we allow the host key to be added. The RPi should display a security
  warning because the default password has not been changed. We will address
  this with Ansible in the next section.
* If you have multiple RPis to configure, get them all to this point before
  proceeding so that the next step can be done in parallel on all RPis at once.

Security and Software Installation
----------------------------------

For this we will use Ansible, which can SSH into one or more RPis in parallel
and automate our work.

* `Install Ansible <https://docs.ansible.com/ansible/devel/installation_guide/intro_installation.html>`_.

* Clone this repository.

  .. code-block:: bash

     git clone https://github.com/danielballan/caproto-rpi
     cd caproto-rpi

* Create an inventory file named ``hosts`` by copying ``hosts.example`` and adding the hostname(s) of the RPi(s) you want to configure.

  .. code-block::

     cp hosts.example hosts
     # Now list the hostname of each RPi under the headers [pis].

* Apply Ansible playbook ``initial_setup.yml``, which will:

  * Harden SSH.
  * Configure a firewall using uncomplicated firewall (``ufw``) that is just
    permissive enough to support SSH and EPICS-related traffic.
  * Get the chip's hardware RNG contributing to system entropy, which is
    necessary for generating enough entropy to importing certain Python packages.
  * Install git and supervisor.
  * Install Python 3.6 from source and install pip using get-pip.py. Building
    Python takes about 60 minutes on a RaspberryPi Zero.
  * Install a new venv with caproto.

  .. code-block:: bash
  
     ansible-playbook initial_setup.yml

* If the RPi will run on battery power, add it to the ``battery-powered`` group
  in ``hosts`` and then apply the ``low_power_usage.yml`` playbook, which should
  shave off 10s of mA of power usage.
  
  .. code-block:: bash
  
     ansible-playbook low_power_usage.yml

* After applying one or both of these playbooks, reboot.
