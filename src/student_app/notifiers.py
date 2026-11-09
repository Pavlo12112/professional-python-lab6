"""Concrete notifier."""


class ConsoleNotifier:
    def send(self, recipient: str, message: str) -> None:
        print(f"[notify -> {recipient}] {message}")
