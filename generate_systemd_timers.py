# /etc/systemd/system/nag_chore@X.timer
TIMER_TEMPLATE = """
[Unit]
Description=Nag {job} on schedule

[Timer]
OnCalendar={timespec}



"""

# /etc/systemd/system/nag_chore@.service
NAG_SERVICE_TEMPLATE = """
[Unit]
Description=status email for %i to user

[Service]
Type=oneshot
ExecStart=curl -X POST -F "chore=%i" {domain}/nag
User=nobody
Group=systemd-journal
"""
