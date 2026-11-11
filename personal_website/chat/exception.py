class UnknownSpeaker(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Chat speaker '{name}' is not defined in the speaker data.")


class UnterminatedChatBlock(Exception):
    def __init__(self, name: str | None) -> None:
        speaker = f"'{name}'" if name else "an anonymous speaker"
        super().__init__(f"Chat block for {speaker} is missing its closing ':::' fence.")
