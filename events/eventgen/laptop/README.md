# Laptop Event Generators

This folder will contain scripts that gather information from laptops and convert it into events. Each operating system has its own subfolder with implementation details.

Possible data sources include:

- Battery level
- CPU and memory usage
- Network status

Scripts should format the data as events so they can be queued to the backend.

The `linux` directory now includes `system_status.py` which emits battery, CPU,
memory and network events. Run it with:

```bash
python linux/system_status.py
```
