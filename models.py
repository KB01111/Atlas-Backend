from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum, JSON, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class AgentFramework(str, enum.Enum):
    OPENAI_ASSISTANT = "OPENAI_ASSISTANT"
    GOOGLE_A2A = "GOOGLE_A2A"
    LITELLM_RAW = "LITELLM_RAW"
    CUSTOM = "CUSTOM"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text)
    framework = Column(Enum(AgentFramework), nullable=False)
    model = Column(String)
    config = Column(JSON)
    plugin_config = Column(JSON)
    avatar_url = Column(String)
    color_theme = Column(String)
    tags = Column(ARRAY(String))
    config_path = Column(String)
    archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())