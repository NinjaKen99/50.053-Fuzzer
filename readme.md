# Spec summary for BLE
```yaml
openble: 0.1.0
info:
  title: string
  # Description in markdown
  description: string
  version: string

services:
  # Service key can be
  # - 16 bit UUID in capital for GATT services: 181A
  # - Long UUID in capital for GATT or custom services: 0000181A-0000-1000-8000-00805F9B34FB
  # - Long identifier: org.bluetooth.service.environmental_sensing
  # - Short identifier: environmental_sensing
  # Identifiers are read from Nordic's UUID database- https://github.com/NordicSemiconductor/bluetooth-numbers-database/tree/master/v1
  environmental_sensing:
    name: Environmental Sensing Service
    summary: Service to read temperature and humidity
    characteristics:
      # Characteristic key is defined similar to service key
      temperature_celsius:
        name: Temperature
        summary: Read or write temperature in Degree Celsius
        # Currently INT32 is the only supported type. TODO support other types
        dataType: INT32
        # READ, WRITE, NOTIFY, INDICATE
        permissions:
          - READ
          - WRITE
      humidity:
        name: Humidity
        summary: Read humidity in percentage. A value of 50 denotes 50% humidity
        dataType: INT32
        permissions:
          - READ
```