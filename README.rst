Headless RPi Setup
------------------

This documentation builds on 
`official docs <https://www.raspberrypi.org/documentation/configuration/wireless/headless.md>`_.

* Download Raspbian Stretch Lite image (no desktop). See
  `Rpi downloads page <https://www.raspberrypi.org/downloads/raspbian/>`_.  
* Use Etcher to "flash" the SD card with this image.
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
  `official docs <https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md`_.
* Check router settings to find RPi's IP address.
* Copy ssh key(s) using ``ssh-copy-id``. The factory default login is
  ``pi``/``raspberry``.
* Set a unique hostname in ``/etc/hostname`` and last line of ``/etc/hosts``.

Create an inventory file named ``hosts`` by copying ``hosts.example`` and
adding the hostname(s) of the RPi(s) you want to configure.

Apply Ansible playbook which will:

* Harden SSH.
* Configure a firewall using uncomplicated firewall (``ufw``) that is just
  permissive enough to support SSH and EPICS-related traffic.
* Install Python 3.6 from source and install pip using get-pip.py. Building
  Python takes about 60 minutes on a RaspberryPi Zero.

.. code-block:: bash

   ansible-playbook initial_setup.yml

Install caproto into a virtual environment:

.. code-block:: bash

   python3.6 -m venv try-caproto
   source try-caproto/bin/activate
   pip install caproto
