def sanitize_branch_name(branch: str) -> str:
    """
    Converts a Git branch name into a safe Docker tag.
    Example: 'feature/login-bug' → 'feature-login-bug'
    """
    return branch.replace("/", "-").replace(" ", "-")
