from sqlalchemy import Column, Integer, LargeBinary, String, Text

from db.database import Base


class ReportWorkflowCheckpointModel(Base):
    __tablename__ = "report_workflow_checkpoint"
    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    checkpoint_id = Column(String, primary_key=True)
    parent_checkpoint_id = Column(String, nullable=True)
    checkpoint_type = Column(String, nullable=False)
    checkpoint_data = Column(LargeBinary, nullable=False)
    metadata_type = Column(String, nullable=False)
    metadata_data = Column(LargeBinary, nullable=False)


class ReportWorkflowCheckpointBlobModel(Base):
    __tablename__ = "report_workflow_checkpoint_blob"

    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    channel = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    value_type = Column(String, nullable=False)
    value = Column(LargeBinary, nullable=False)


class ReportWorkflowCheckpointWriteModel(Base):
    __tablename__ = "report_workflow_checkpoint_write"
    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    checkpoint_id = Column(String, primary_key=True)
    task_id = Column(String, primary_key=True)
    idx = Column(Integer, primary_key=True)
    channel = Column(String, nullable=False)
    value_type = Column(String, nullable=False)
    value = Column(LargeBinary, nullable=False)
    task_path = Column(Text, nullable=False, default="")
