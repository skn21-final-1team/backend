import random
from collections.abc import Sequence
from typing import Any

from langchain_core.runnables import RunnableConfig
from sqlalchemy import delete, select, tuple_
from sqlalchemy.orm import Session

from db.database import get_db_context
from langgraph.checkpoint.base import (
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
    get_checkpoint_id,
    get_checkpoint_metadata,
)
from models.report_workflow_checkpoint import (
    ReportWorkflowCheckpointBlobModel,
    ReportWorkflowCheckpointModel,
    ReportWorkflowCheckpointWriteModel,
)


class ReportWorkflowCheckpointSaver(BaseCheckpointSaver[str]):
    def _load_channel_values(
        self,
        session: Session,
        thread_id: str,
        checkpoint_ns: str,
        versions: ChannelVersions,
    ) -> dict[str, Any]:
        if not versions:
            return {}

        rows = session.execute(
            select(ReportWorkflowCheckpointBlobModel).where(
                ReportWorkflowCheckpointBlobModel.thread_id == thread_id,
                ReportWorkflowCheckpointBlobModel.checkpoint_ns == checkpoint_ns,
                tuple_(
                    ReportWorkflowCheckpointBlobModel.channel,
                    ReportWorkflowCheckpointBlobModel.version,
                ).in_([(channel, str(version)) for channel, version in versions.items()]),
            )
        ).scalars().all()

        rows_by_key = {(row.channel, row.version): row for row in rows}
        return {
            channel: self.serde.loads_typed((row.value_type, row.value))
            for channel, version in versions.items()
            if (row := rows_by_key.get((channel, str(version)))) is not None and row.value_type != "empty"
        }

    def _load_pending_writes(
        self,
        session: Session,
        thread_id: str,
        checkpoint_ns: str,
        checkpoint_id: str,
    ) -> list[PendingWrite]:
        rows = session.execute(
            select(ReportWorkflowCheckpointWriteModel).where(
                ReportWorkflowCheckpointWriteModel.thread_id == thread_id,
                ReportWorkflowCheckpointWriteModel.checkpoint_ns == checkpoint_ns,
                ReportWorkflowCheckpointWriteModel.checkpoint_id == checkpoint_id,
            ).order_by(
                ReportWorkflowCheckpointWriteModel.task_id,
                ReportWorkflowCheckpointWriteModel.idx,
            )
        ).scalars().all()

        return [
            (row.task_id, row.channel, self.serde.loads_typed((row.value_type, row.value)))
            for row in rows
        ]

    def _to_checkpoint_tuple(
        self,
        session: Session,
        row: ReportWorkflowCheckpointModel,
    ) -> CheckpointTuple:
        checkpoint = self.serde.loads_typed((row.checkpoint_type, row.checkpoint_data))
        checkpoint_ns = row.checkpoint_ns or ""
        checkpoint["channel_values"] = self._load_channel_values(
            session,
            row.thread_id,
            checkpoint_ns,
            checkpoint["channel_versions"],
        )

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": row.thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": row.checkpoint_id,
                }
            },
            checkpoint=checkpoint,
            metadata=self.serde.loads_typed((row.metadata_type, row.metadata_data)),
            parent_config=(
                None
                if row.parent_checkpoint_id is None
                else {
                    "configurable": {
                        "thread_id": row.thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": row.parent_checkpoint_id,
                    }
                }
            ),
            pending_writes=self._load_pending_writes(
                session,
                row.thread_id,
                checkpoint_ns,
                row.checkpoint_id,
            ),
        )

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        thread_id = str(config["configurable"]["thread_id"])
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)

        with get_db_context() as session:
            stmt = select(ReportWorkflowCheckpointModel).where(
                ReportWorkflowCheckpointModel.thread_id == thread_id,
                ReportWorkflowCheckpointModel.checkpoint_ns == checkpoint_ns,
            )
            if checkpoint_id is None:
                stmt = stmt.order_by(ReportWorkflowCheckpointModel.checkpoint_id.desc()).limit(1)
            else:
                stmt = stmt.where(ReportWorkflowCheckpointModel.checkpoint_id == checkpoint_id)

            row = session.execute(stmt).scalars().first()
            if row is None:
                return None

            return self._to_checkpoint_tuple(session, row)

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        return self.get_tuple(config)

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread_id = str(config["configurable"]["thread_id"])
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_to_store = checkpoint.copy()
        channel_values = checkpoint_to_store.pop("channel_values")
        checkpoint_type, checkpoint_data = self.serde.dumps_typed(checkpoint_to_store)
        metadata_type, metadata_data = self.serde.dumps_typed(
            get_checkpoint_metadata(config, metadata)
        )

        with get_db_context() as session:
            for channel, version in new_versions.items():
                value_type, value = (
                    self.serde.dumps_typed(channel_values[channel])
                    if channel in channel_values
                    else ("empty", b"")
                )
                session.merge(
                    ReportWorkflowCheckpointBlobModel(
                        thread_id=thread_id,
                        checkpoint_ns=checkpoint_ns,
                        channel=channel,
                        version=str(version),
                        value_type=value_type,
                        value=value,
                    )
                )

            session.merge(
                ReportWorkflowCheckpointModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint["id"],
                    parent_checkpoint_id=config["configurable"].get("checkpoint_id"),
                    checkpoint_type=checkpoint_type,
                    checkpoint_data=checkpoint_data,
                    metadata_type=metadata_type,
                    metadata_data=metadata_data,
                )
            )
            session.commit()

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint["id"],
            }
        }

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        return self.put(config, checkpoint, metadata, new_versions)

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        thread_id = str(config["configurable"]["thread_id"])
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]

        with get_db_context() as session:
            for idx, (channel, value) in enumerate(writes):
                write_index = WRITES_IDX_MAP.get(channel, idx)
                row = session.execute(
                    select(ReportWorkflowCheckpointWriteModel).where(
                        ReportWorkflowCheckpointWriteModel.thread_id == thread_id,
                        ReportWorkflowCheckpointWriteModel.checkpoint_ns == checkpoint_ns,
                        ReportWorkflowCheckpointWriteModel.checkpoint_id == checkpoint_id,
                        ReportWorkflowCheckpointWriteModel.task_id == task_id,
                        ReportWorkflowCheckpointWriteModel.idx == write_index,
                    )
                ).scalars().first()

                if write_index >= 0 and row is not None:
                    continue

                value_type, value_bytes = self.serde.dumps_typed(value)
                if row is None:
                    row = ReportWorkflowCheckpointWriteModel(
                        thread_id=thread_id,
                        checkpoint_ns=checkpoint_ns,
                        checkpoint_id=checkpoint_id,
                        task_id=task_id,
                        idx=write_index,
                    )
                    session.add(row)

                row.channel = channel
                row.value_type = value_type
                row.value = value_bytes
                row.task_path = task_path

            session.commit()

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        self.put_writes(config, writes, task_id, task_path)

    def delete_thread(self, thread_id: str) -> None:
        with get_db_context() as session:
            session.execute(
                delete(ReportWorkflowCheckpointWriteModel).where(
                    ReportWorkflowCheckpointWriteModel.thread_id == thread_id
                )
            )
            session.execute(
                delete(ReportWorkflowCheckpointBlobModel).where(
                    ReportWorkflowCheckpointBlobModel.thread_id == thread_id
                )
            )
            session.execute(
                delete(ReportWorkflowCheckpointModel).where(
                    ReportWorkflowCheckpointModel.thread_id == thread_id
                )
            )
            session.commit()

    def get_next_version(self, current: str | None, channel: None) -> str:
        current_version = 0 if current is None else int(str(current).split(".")[0])
        return f"{current_version + 1:032}.{random.random():016}"


report_workflow_checkpoint_saver = ReportWorkflowCheckpointSaver()
