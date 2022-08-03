from typing import List


class AISRecord:

    def __init__(self, timestamp: int, mmsi: int, latitude: float, longitude: float, sog: float) -> None:
        super().__init__()
        self.timestamp = timestamp
        self.mmsi = mmsi
        self.latitude = latitude
        self.longitude = longitude
        self.sog = sog


class MMSI_instants:

    def __init__(self, mmsi: int, instants: List) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.instants = instants


def main():
    pass


if __name__ == '__main__':
    main()
