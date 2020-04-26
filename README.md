# SSH Login Notifications via Twilio

Send an SMS message when someone logs into a server using [Twilio](https://www.twilio.com), [Python 3](https://www.python.org/), and [Systemd Journal](https://wiki.archlinux.org/index.php/Systemd/Journal) for logging

## Prerequisites

### Install Python Virtual Environment and Systemd Development Packages

#### Centos/RHEL Based Distritbutions

```bash
yum install -y python-virtualenv python36-virtualenv systemd-devel
```

#### Debian/Ubuntu Based Distritbutions

```bash
apt install -y virtualenv python3-virtualenv build-essential libsystemd-journal-dev libsystemd-daemon-dev libsystemd-dev
```

## Configuration

Download content of repo to a directory of your choosing.

### Activate Python Virtual Environment and Install Dependencies

Build a virtual work environment for Python and install the [requirements](requirements.txt).

```bash
cd <repo content directory>
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Copy Existing 'secrets.env.example' to '.secrets.env'

Copy the existing [secrets.env.example](secrets.env.example) file within the repo content directory to a new [.secrets.env](secrets.env.example) file as references within the [ssh-login-notify.service.example](ssh-login-notify.service.example) file.

Change the permissions on the new [.secrets.env](secrets.env.example) file so that no one except you can read the content.

```bash
cp <repo content directory>/secrets.env.example <repo content directory>/.secrets.env
chmod 0660 <repo content directory>/.secrets.env
```

### Update Content of New '.secrets.env' File

#### Secrets Environment Variable Content:

| Environment Variable | Description                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SSH_AUTH_FILE        | This will be the path to the SSH log file. Centos/RHEL should be /var/log/secure and Debian/Ubuntu should be /var/log/auth.log                                |
| TARGET_SMS_NUMBER    | This will be the cell phone number that should receive text messages about SSH logins                                                                         |
| TWILIO_ACCOUNT_SID   | This will be your Twilio Account SID which can be found on the main Twilio console page [here](https://www.twilio.com/console)                                |
| TWILIO_AUTH_TOKEN    | This will be your Twilio Auth Token which can be found on the main Twilio console page [here](https://www.twilio.com/console)                                 |
| TWILIO_MSG_SID       | This will be your Twilio SMS Messaging Service SID which can be found on the programable SMS console page [here](https://www.twilio.com/console/sms/services) |

### Copy Existing 'ssh-login-notify.service.example' to 'ssh-login-notify.service'

Copy the existing [ssh-login-notify.service.example](ssh-login-notify.service.example) file within the repo content directory to a new [ssh-login-notify.service](ssh-login-notify.service.example) file.

```bash
cp <repo content directory>/ssh-login-notify.service.example <repo content directory>/ssh-login-notify.service
```

Edit the new 'ssh-login-notify.service' file and update the relevent directory paths to point to the repo content directory you've been working in.

### Create Symlink for Systemd Service, Reload Systemd Daemon, Start the Service, and Enable Start on Boot

```bash
ln -s <repo content directory>/ssh-login-notify/ssh-login-notify.service /etc/systemd/system/multi-user.target.wants/ssh-login-notify.service
systemctl daemon-reload
systemctl start ssh-login-notify.service
systemctl enable ssh-login-notify.service
```
