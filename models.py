"""Pydantic models for form input validation."""

from pydantic import BaseModel, field_validator

from config import CONCERNS, EXTRAS, RELATIONSHIPS, TONES, VIBES, YEARS_OPTIONS
from utils import sanitize_freetext


class CommentRequest(BaseModel):
    name: str = ""
    address: str = ""
    concerns: list[str] = []
    vibe: str = "concerned"
    tone: str = "conversational"
    relationship: str = ""
    years: str = ""
    extras: list[str] = []
    custom_note: str = ""

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return sanitize_freetext(v, 100)

    @field_validator("address")
    @classmethod
    def sanitize_address(cls, v: str) -> str:
        return sanitize_freetext(v, 200)

    @field_validator("custom_note")
    @classmethod
    def sanitize_custom_note(cls, v: str) -> str:
        return sanitize_freetext(v, 500)

    @field_validator("concerns")
    @classmethod
    def filter_concerns(cls, v: list[str]) -> list[str]:
        return [c for c in v if c in CONCERNS]

    @field_validator("extras")
    @classmethod
    def filter_extras(cls, v: list[str]) -> list[str]:
        return [e for e in v if e in EXTRAS]

    @field_validator("vibe")
    @classmethod
    def validate_vibe(cls, v: str) -> str:
        return v if v in VIBES else "concerned"

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        return v if v in TONES else "conversational"

    @field_validator("relationship")
    @classmethod
    def validate_relationship(cls, v: str) -> str:
        return v if v in RELATIONSHIPS else ""

    @field_validator("years")
    @classmethod
    def validate_years(cls, v: str) -> str:
        return v if v in YEARS_OPTIONS else ""

    @property
    def concern_text(self) -> str:
        if not self.concerns:
            return "general opposition to the rezoning"
        return ", ".join(CONCERNS[k][1] for k in self.concerns)

    @property
    def vibe_instruction(self) -> str:
        return VIBES[self.vibe][2]

    @property
    def tone_instruction(self) -> str:
        return TONES[self.tone][1]

    @property
    def relationship_label(self) -> str:
        if not self.relationship:
            return "resident"
        return RELATIONSHIPS[self.relationship][1]

    @property
    def years_description(self) -> str:
        if not self.years:
            return "who lives in"
        return YEARS_OPTIONS[self.years][1]

    @property
    def extras_text(self) -> str:
        if not self.extras:
            return "None"
        return "\n".join(f"- {EXTRAS[k][1]}" for k in self.extras)
