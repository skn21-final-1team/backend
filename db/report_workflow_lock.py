from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import text

from core.exceptions.report import ReportWorkflowAlreadyRunningException
from db.database import engine

_REPORT_WORKFLOW_LOCK_NAMESPACE = 48159


@contextmanager
def acquire_report_workflow_lock(notebook_id: int) -> Generator[None]:
    with engine.connect() as connection:
        acquired = connection.execute(
            text(
                "SELECT pg_try_advisory_lock(:lock_namespace, :notebook_id)"
            ),
            {
                "lock_namespace": _REPORT_WORKFLOW_LOCK_NAMESPACE,
                "notebook_id": notebook_id,
            },
        ).scalar_one()
        connection.commit()

        if not acquired:
            raise ReportWorkflowAlreadyRunningException()

        try:
            yield
        finally:
            connection.execute(
                text(
                    "SELECT pg_advisory_unlock(:lock_namespace, :notebook_id)"
                ),
                {
                    "lock_namespace": _REPORT_WORKFLOW_LOCK_NAMESPACE,
                    "notebook_id": notebook_id,
                },
            )
            connection.commit()
