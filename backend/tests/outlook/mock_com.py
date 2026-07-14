from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MockAttachment:
    FileName: str = "test.txt"

    def SaveAsFile(self, path: str) -> None:
        pass


@dataclass
class MockMailItem:
    ConversationID: str = "conv-123"
    EntryID: str = "entry-001"
    SenderName: str = "Test Sender"
    Subject: str = "Test Subject"
    Body: str = "Test Body"
    ReceivedTime: datetime = field(default_factory=datetime.now)
    UnRead: bool = True
    Attachments: Any = field(default_factory=lambda: MockAttachments())

    def Reply(self) -> MockMailItem:
        return MockMailItem(
            ConversationID=self.ConversationID,
            EntryID=f"{self.EntryID}-reply",
            Subject=f"RE: {self.Subject}",
            Body="",
        )

    def Send(self) -> None:
        pass


@dataclass
class MockAttachments:
    Count: int = 0
    items: list[MockAttachment] = field(default_factory=list)

    def Item(self, index: int) -> MockAttachment:
        return self.items[index - 1] if index <= len(self.items) else MockAttachment()


@dataclass
class MockItems:
    items: list[MockMailItem] = field(default_factory=list)

    @property
    def Count(self) -> int:
        return len(self.items)

    def Restrict(self, filter_str: str) -> MockItems:
        if "UnRead" in filter_str:
            filtered = [m for m in self.items if m.UnRead]
        elif "ConversationID" in filter_str:
            conv_id = filter_str.split("'")[1]
            filtered = [m for m in self.items if m.ConversationID == conv_id]
        else:
            filtered = self.items
        return MockItems(items=filtered)

    def Sort(self, field: str, descending: bool = False) -> None:
        self.items.sort(key=lambda m: getattr(m, field.replace("[", "").replace("]", ""), ""), reverse=descending)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


@dataclass
class MockInbox:
    items: MockItems = field(default_factory=MockItems)

    @property
    def Items(self) -> MockItems:
        return self.items


@dataclass
class MockAppointmentItem:
    EntryID: str = "appt-001"
    Subject: str = "Test Event"
    Start: datetime = field(default_factory=datetime.now)
    End: datetime = field(default_factory=lambda: datetime.now())
    Body: str = ""
    AllDayEvent: bool = False
    ReminderSet: bool = False
    ReminderMinutesBeforeStart: int = 15

    def Save(self) -> None:
        pass

    def Send(self) -> None:
        pass

    def Delete(self) -> None:
        pass


@dataclass
class MockCalendarItems:
    items: list[MockAppointmentItem] = field(default_factory=list)
    IncludeRecurrences: bool = False

    def Restrict(self, filter_str: str) -> MockCalendarItems:
        return MockCalendarItems(items=self.items, IncludeRecurrences=self.IncludeRecurrences)

    def Sort(self, field: str) -> None:
        pass

    def Add(self) -> MockAppointmentItem:
        item = MockAppointmentItem()
        self.items.append(item)
        return item

    def __iter__(self):
        return iter(self.items)


@dataclass
class MockCalendar:
    _items: MockCalendarItems = field(default_factory=MockCalendarItems)

    @property
    def Items(self) -> MockCalendarItems:
        return self._items


@dataclass
class MockNamespace:
    _inbox: MockInbox = field(default_factory=MockInbox)
    _calendar: MockCalendar = field(default_factory=MockCalendar)

    def GetDefaultFolder(self, folder_type: int) -> Any:
        if folder_type == 6:
            return self._inbox
        elif folder_type == 9:
            return self._calendar
        raise ValueError(f"Unknown folder type: {folder_type}")

    def GetItemFromID(self, entry_id: str) -> MockMailItem | MockAppointmentItem:
        for item in self._inbox.items:
            if item.EntryID == entry_id:
                return item
        for item in self._calendar._items.items:
            if item.EntryID == entry_id:
                return item
        raise ValueError(f"Item not found: {entry_id}")


@dataclass
class MockOutlookApp:
    _namespace: MockNamespace = field(default_factory=MockNamespace)

    def GetNamespace(self, name: str) -> MockNamespace:
        return self._namespace
