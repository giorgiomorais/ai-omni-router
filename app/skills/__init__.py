"""
Skills package init: imports all skills so they are self-registered into skill_registry.
"""
from app.skills.base import skill_registry
import app.skills.finance_skills
import app.skills.data_skills
import app.skills.chart_skills

__all__ = ["skill_registry"]
