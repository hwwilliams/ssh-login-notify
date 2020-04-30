# SSH Login Notifications via Twilio

Send an SMS message when someone logs into a Linux server using SSH. Notify with SMS using [Twilio](https://www.twilio.com), written in [Python 3](https://www.python.org/), and [Systemd Journal](https://wiki.archlinux.org/index.php/Systemd/Journal) for logging.

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

### Copy Existing 'contacts.json.example' to 'contacts.json'

Copy the existing [contacts.json.example](settings/contacts.json.example) file within the settings folder of the repo content directory to a new [contacts.json](settings/contacts.json.example) file.

```bash
cp <repo content directory>/settings/contacts.json.example <repo content directory>/settings/contacts.json
```

Edit and update the contact information within the [contacts.json](settings/contacts.json.example) file, make sure the phone number is in the [correct format](https://www.twilio.com/docs/glossary/what-e164) for Twilio to understand.

### Copy Existing 'log_file.json.example' to 'log_file.json'

Copy the existing [log_file.json.example](settings/log_file.json.example) file within the settings folder of the repo content directory to a new [log_file.json](settings/log_file.json.example) file.

```bash
cp <repo content directory>/settings/log_file.json.example <repo content directory>/settings/log_file.json
```

Edit and update the log path, depending on the distribution you're using the log file may be in a different place under a different name.

#### Distribution Log Locations

**Centos/RHEL**: /var/log/secure

**Debian/Ubuntu**: /var/log/auth.log

### Copy Existing 'secrets.env.example' to 'secrets.env'

Copy the existing [secrets.env.example](settings/secrets.env.example) file within  the settings folder of the repo content directory to a new [secrets.env](settings/secrets.env.example) file.

```bash
cp <repo content directory>/settings/secrets.env.example <repo content directory>/settings/secrets.env
```

Change the permissions on the new [secrets.env](settings/secrets.env.example) file so that no one except you can read the content.

```bash
chmod 0600 <repo content directory>/settings/secrets.env
```

### Update Content of New '.secrets.env' File

#### Secrets Environment Variable Content:

| Environment Variable   | Description                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TWILIO_ACCOUNT_SID     | This will be your Twilio Account SID which can be found on the main Twilio console page [here](https://www.twilio.com/console)                                |
| TWILIO_AUTH_TOKEN      | This will be your Twilio Auth Token which can be found on the main Twilio console page [here](https://www.twilio.com/console)                                 |
| TWILIO_MSG_SERVICE_SID | This will be your Twilio SMS Messaging Service SID which can be found on the programable SMS console page [here](https://www.twilio.com/console/sms/services) |

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
