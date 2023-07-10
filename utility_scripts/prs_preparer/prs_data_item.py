from dataclasses import dataclass

@dataclass
class PrsDataItem:
    file:str = ""
    description:str = ""
    name:str = ""
    revers:int = 0