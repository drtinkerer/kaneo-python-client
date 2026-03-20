from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Config:
    disable_registration: bool
    is_demo_mode: bool
    has_smtp: bool
    has_github_sign_in: bool
    has_google_sign_in: bool
    has_discord_sign_in: bool
    has_custom_oauth: bool
    has_guest_access: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        return cls(
            disable_registration=data.get("disableRegistration", False),
            is_demo_mode=data.get("isDemoMode", False),
            has_smtp=data.get("hasSmtp", False),
            has_github_sign_in=data.get("hasGithubSignIn", False),
            has_google_sign_in=data.get("hasGoogleSignIn", False),
            has_discord_sign_in=data.get("hasDiscordSignIn", False),
            has_custom_oauth=data.get("hasCustomOAuth", False),
            has_guest_access=data.get("hasGuestAccess", False),
        )
