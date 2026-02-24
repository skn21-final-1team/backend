from sqlalchemy.orm import Session

from crud.directory import get_directories_by_notebook
from crud.source import get_sources_by_notebook
from schemas.directory import DirectoryResponse, DirectoryTreeResponse, SourceResponse


class DirectoryService:
    """디렉토리 트리를 구성하는 역활을 담당하는 서비스 클래스"""

    def get_directory_tree(self, db: Session, notebook_id: int) -> DirectoryTreeResponse:
        """
        notebook_id에 해당하는 모든 디렉토리와 소스를 DB에서 조회한 후폴더 트리(Tree) 구조로 가공하여 반환합니다.

        Args:
            notebook_id (int): 탐색할 기준이 되는 노트북 ID

        Returns:
            DirectoryTreeResponse: 구성된 전체 트리 정보 모델
        """
        directories = get_directories_by_notebook(db, notebook_id)
        sources = get_sources_by_notebook(db, notebook_id)

        dir_dict: dict[int, DirectoryResponse] = {}
        for d in directories:
            node = DirectoryResponse.model_validate(d)
            # 매번 새로운 리스트 인스턴스가 할당됨을 완벽히 보장하기 위해 명시적 초기화
            node.children = []
            node.sources = []
            dir_dict[node.id] = node

        unassigned_sources: list[SourceResponse] = []
        for s in sources:
            source_node = SourceResponse.model_validate(s)

            if source_node.directory_id is None or source_node.directory_id not in dir_dict:
                unassigned_sources.append(source_node)
                continue

            dir_dict[source_node.directory_id].sources.append(source_node)

        root_directories: list[DirectoryResponse] = []
        for node in dir_dict.values():
            if node.parent_id is None or node.parent_id not in dir_dict:
                root_directories.append(node)
                continue

            dir_dict[node.parent_id].children.append(node)

        return DirectoryTreeResponse(
            directories=root_directories,
            sources=unassigned_sources,
        )


directory_service = DirectoryService()
