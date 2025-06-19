# USB Monitoring Agent

This project provides a Python agent intended for Windows 10/11 systems. It
monitors USB insertion/removal events, scans transferred files for sensitive
content, and logs activity. If sensitive content is detected or an archive is
transferred, the agent requests approval from another machine.

The agent copies processed files to network folders representing a Raspberry Pi
for record keeping (`SAFE` or `ALERT`).

## Requirements

- Python 3.8+
- Packages listed in `requirements.txt`
- Windows OS with `pywin32` installed

## Running

```bash
pip install -r requirements.txt
python -m usb_agent.main
```

The agent runs indefinitely and logs to `logs/usb.log`.
