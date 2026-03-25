"""Git代码同步模块

该模块提供Git仓库同步功能，用于CLI执行前自动拉取最新代码。
"""

import subprocess
import os
import logging

logger = logging.getLogger(__name__)


class GitSyncModule:
    """Git代码同步模块

    用于在CLI执行前自动执行git pull，确保代码是最新版本。
    支持以下两种目录结构：
    - working_dir 本身是 Git 仓库
    - working_dir 的一级子目录包含一个或多个 Git 仓库

    Attributes:
        enabled: 是否启用自动同步
        timeout: git pull超时时间（秒）
    """

    def __init__(self, enabled: bool = True, timeout: int = 30):
        """初始化Git同步模块

        Args:
            enabled: 是否启用自动同步，默认为True
            timeout: git pull超时时间（秒），默认为30秒
        """
        self.enabled = enabled
        self.timeout = timeout

    def is_git_repo(self, working_dir: str) -> bool:
        """检查目录是否为有效的Git仓库

        Args:
            working_dir: 要检查的工作目录路径

        Returns:
            如果是有效的Git仓库返回True，否则返回False
        """
        if not os.path.exists(working_dir):
            return False

        git_dir = os.path.join(working_dir, ".git")
        return os.path.isdir(git_dir)

    def find_git_repos(self, working_dir: str) -> list[str]:
        """查找可同步的 Git 仓库路径。

        规则：
        1) 如果 working_dir 本身是 Git 仓库，则仅返回该目录。
        2) 否则扫描其一级子目录，返回所有 Git 仓库。

        Args:
            working_dir: 工作目录路径

        Returns:
            Git 仓库路径列表
        """
        if not os.path.isdir(working_dir):
            return []

        if self.is_git_repo(working_dir):
            return [working_dir]

        repos: list[str] = []
        try:
            for entry in os.scandir(working_dir):
                if entry.is_dir(follow_symlinks=False) and self.is_git_repo(entry.path):
                    repos.append(entry.path)
        except PermissionError as err:
            logger.warning(f"扫描子目录权限不足: {err}")

        return repos

    def _pull_one_repo(self, repo_dir: str) -> tuple[bool, str]:
        """对单个 Git 仓库执行 git pull。"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            output = (result.stdout or "") + (result.stderr or "")
            if result.returncode == 0:
                logger.info(f"Git sync completed for {repo_dir}")
                logger.debug(f"Git pull output: {output}")
                return True, output

            logger.error(f"Git pull failed for {repo_dir}: {output}")
            return False, f"Git pull失败: {output}"

        except subprocess.TimeoutExpired:
            msg = f"Git pull超时(>{self.timeout}s): {repo_dir}"
            logger.error(msg)
            return False, msg
        except Exception as err:
            msg = f"Git同步错误: {repo_dir}: {err}"
            logger.error(msg)
            return False, msg

    def sync(self, working_dir: str) -> tuple[bool, str]:
        """同步代码（执行 git pull）。

        Args:
            working_dir: 工作目录路径

        Returns:
            元组 (是否成功, 输出信息)
            - 成功: (True, 汇总输出)
            - 失败但继续: (True, 错误信息) - 失败不中断后续执行
        """
        if not self.enabled:
            logger.info("Git同步已禁用")
            return True, "Git同步已禁用"

        repos = self.find_git_repos(working_dir)
        if not repos:
            logger.warning(f"{working_dir} 及其一级子目录中未找到Git仓库，跳过同步")
            return True, "未找到Git仓库，跳过同步"

        summary_lines: list[str] = []
        for repo_dir in repos:
            ok, message = self._pull_one_repo(repo_dir)
            prefix = "[OK]" if ok else "[FAIL]"
            summary_lines.append(f"{prefix} {repo_dir}: {message.strip()}")

            if not ok:
                logger.warning(f"Git sync failed but continuing: {repo_dir}")

        summary = "\n".join(summary_lines)
        logger.debug(f"Git sync summary:\n{summary}")

        # 与现有执行链保持兼容：即使部分仓库失败也不阻断后续 CLI 执行
        return True, summary
