from pathlib import Path


class CannotFindDecompRepoError(Exception):
    pass


def find_decomp_repo(export_directory: Path):
    candidate_decomp_repo_p = export_directory.resolve()
    while not (candidate_decomp_repo_p / "spec").exists():
        parent_p = candidate_decomp_repo_p.parent
        if parent_p == candidate_decomp_repo_p:
            raise CannotFindDecompRepoError
        candidate_decomp_repo_p = parent_p
    decomp_repo_p = candidate_decomp_repo_p
    return decomp_repo_p
