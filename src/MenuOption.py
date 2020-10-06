from typing import Callable, List


class MenuOption:
    def __init__(self, title: str, desc: str, handler: Callable[[], None]):
        self.title = title
        self.desc = desc
        self.handler = handler


class MenuOptionList:

    def __init__(self):
        self.listing: List[MenuOption] = []

    def add(self, title: str, desc: str, handler: Callable[[], None]):
        self.listing.append(MenuOption(title, desc, handler))

    def remove(self, title: str):
        self.listing = list(filter(lambda c: c.title != title, self.listing))

    def to_title_list(self) -> List[str]:
        return list(map(lambda opt: opt.title, self.listing))

    def print_options(self) -> None:
        for item in self.listing:
            print(item.title, ": ", item.desc)

    def __contains__(self, title: str):
        valid = list(filter(lambda c: c.title == title, self.listing))
        return len(valid) > 0

    def __getitem__(self, title):
        valid = list(filter(lambda c: c.title == title, self.listing))
        assert len(valid) == 1
        return valid[0]
