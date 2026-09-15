class Whitener:
    @staticmethod
    def __call__(xml_string: str) -> str:
        """
        Strip each line and concatenate an XML fragment.

        Intended for MJCF fragments without meaningful element text.

        Args:
            xml_string (str): The original XML string.

        Returns:
            str: The minimized XML string.
        """
        text = xml_string.split("\n")
        return "".join([line.strip() for line in text])

    def __ror__(self, s: str) -> str:
        return self(s)


whiten = Whitener()
