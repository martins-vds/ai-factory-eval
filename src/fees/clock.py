from datetime import date


class ServerLocalClock:
    def today(self) -> date:
        return date.today()
