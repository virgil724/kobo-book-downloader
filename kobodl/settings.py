import json
import os
from typing import List, Union

from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError
from pydantic.json import pydantic_encoder
from pydantic.networks import HttpUrl


class CalibreWeb(BaseModel):
    enabled: bool = False
    url: HttpUrl = "http://localhost:8083"
    username: str = ""
    password: str = ""


class User(BaseModel):
    Email: str
    DeviceId: str = ""
    AccessToken: str = ""
    RefreshToken: str = ""
    UserId: str = ""
    UserKey: str = ""

    def AreAuthenticationSettingsSet(self) -> bool:
        return len(self.DeviceId) > 0 and len(self.AccessToken) > 0 and len(self.RefreshToken) > 0

    def IsLoggedIn(self) -> bool:
        return len(self.UserId) > 0 and len(self.UserKey) > 0


class UserList(BaseModel):
    users: List[User] = Field(default_factory=list)
    calibre_web: CalibreWeb = Field(default_factory=CalibreWeb)

    def getUser(self, identifier: str) -> Union[User, None]:
        for user in self.users:
            if (
                user.Email == identifier
                or user.UserKey == identifier
                or user.DeviceId == identifier
            ):
                return user
        return None

    def removeUser(self, identifier: str) -> Union[User, None]:
        """returns the removed user"""
        user = self.getUser(identifier)
        if user:
            i = self.users.index(user)
            return self.users.pop(i)
        return None


class Settings:
    def __init__(self, configpath=None):
        self.SettingsFilePath = configpath or Settings.__GetCacheFilePath()
        self.UserList = self.Load()

    def Load(self) -> UserList:
        if not os.path.isfile(self.SettingsFilePath):
            return UserList()
        with open(self.SettingsFilePath, "r") as settings_file:
            settings_dict = json.load(settings_file)
            return UserList(**settings_dict)

    def Save(self) -> None:
        with open(self.SettingsFilePath, "w") as f:
            json.dump(self.UserList, f, indent=4, default=pydantic_encoder)

    @staticmethod
    def __GetCacheFilePath() -> str:
        cacheHome = os.environ.get("XDG_CONFIG_HOME")
        if (cacheHome is None) or (not os.path.isdir(cacheHome)):
            home = os.path.expanduser("~")
            cacheHome = os.path.join(home, ".config")
            if not os.path.isdir(cacheHome):
                cacheHome = home

        return os.path.join(cacheHome, "kobodl.json")
