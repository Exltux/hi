from .usb_monitor import USBMonitor


def main():
    monitor = USBMonitor()
    monitor.poll_drives()


if __name__ == "__main__":
    main()
