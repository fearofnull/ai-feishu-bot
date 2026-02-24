"""
临时目录生命周期属性测试

使用 Hypothesis 进行基于属性的测试，验证 TempConfigManager 正确管理临时配置目录的通用正确性属性。
测试临时目录的创建、环境变量设置和清理行为。
"""
import os
import tempfile
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.temp_config_manager import TempConfigManager


class TestTempConfigLifecycleProperties:
    """临时目录生命周期属性测试类"""
    
    # Feature: feishu-ai-bot, Property 10: 临时目录生命周期
    # Validates: Requirements 4.1, 4.2, 4.3
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_temp_directory_created_with_claude_prefix(self, iterations):
        """
        Property 10: 临时目录生命周期 - 临时目录使用 "claude_" 前缀创建
        
        For any execution of TempConfigManager, the temporary directory
        should be created with "claude_" prefix.
        
        Validates: Requirement 4.1
        """
        for _ in range(iterations):
            with TempConfigManager() as temp_dir:
                # Verify directory exists
                assert os.path.exists(temp_dir), \
                    f"Temporary directory should exist: {temp_dir}"
                
                # Verify directory is actually a directory
                assert os.path.isdir(temp_dir), \
                    f"Path should be a directory: {temp_dir}"
                
                # Verify directory name has "claude_" prefix
                dir_name = os.path.basename(temp_dir)
                assert dir_name.startswith("claude_"), \
                    f"Directory name should start with 'claude_', got: {dir_name}"
                
                # Verify it's in the system temp directory
                temp_root = tempfile.gettempdir()
                assert temp_dir.startswith(temp_root), \
                    f"Directory should be in system temp directory {temp_root}, got: {temp_dir}"
            
            # After context exit, directory should be deleted
            assert not os.path.exists(temp_dir), \
                f"Temporary directory should be deleted after context exit: {temp_dir}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_claude_config_dir_environment_variable_set(self, iterations):
        """
        Property 10: 临时目录生命周期 - CLAUDE_CONFIG_DIR 环境变量正确设置
        
        For any execution of TempConfigManager, the CLAUDE_CONFIG_DIR
        environment variable should be set to point to the temporary directory
        during the context, and restored/removed after exit.
        
        Validates: Requirement 4.2
        """
        # Save original environment variable state
        original_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        
        for _ in range(iterations):
            with TempConfigManager() as temp_dir:
                # Verify CLAUDE_CONFIG_DIR is set
                assert "CLAUDE_CONFIG_DIR" in os.environ, \
                    "CLAUDE_CONFIG_DIR environment variable should be set"
                
                # Verify it points to the temporary directory
                config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
                assert config_dir == temp_dir, \
                    f"CLAUDE_CONFIG_DIR should point to temp directory. Expected: {temp_dir}, Got: {config_dir}"
                
                # Verify the directory exists
                assert os.path.exists(config_dir), \
                    f"CLAUDE_CONFIG_DIR should point to existing directory: {config_dir}"
            
            # After context exit, verify environment variable is restored
            current_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
            if original_config_dir is None:
                # If it wasn't set originally, it should be removed
                assert current_config_dir is None, \
                    f"CLAUDE_CONFIG_DIR should be removed after context exit, but got: {current_config_dir}"
            else:
                # If it was set originally, it should be restored
                assert current_config_dir == original_config_dir, \
                    f"CLAUDE_CONFIG_DIR should be restored to original value. Expected: {original_config_dir}, Got: {current_config_dir}"
        
        # Restore original state for other tests
        if original_config_dir is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = original_config_dir
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_temp_directory_deleted_after_context_exit(self, iterations):
        """
        Property 10: 临时目录生命周期 - 临时目录在上下文退出后被删除
        
        For any execution of TempConfigManager, the temporary directory
        should be deleted after the context manager exits, regardless of
        whether execution was successful or an exception occurred.
        
        Validates: Requirement 4.3
        """
        temp_dirs_created = []
        
        for _ in range(iterations):
            # Test successful execution
            with TempConfigManager() as temp_dir:
                temp_dirs_created.append(temp_dir)
                assert os.path.exists(temp_dir), \
                    f"Directory should exist during context: {temp_dir}"
            
            # Verify cleanup after successful execution
            assert not os.path.exists(temp_dir), \
                f"Directory should be deleted after successful execution: {temp_dir}"
        
        # Verify all directories were cleaned up
        for temp_dir in temp_dirs_created:
            assert not os.path.exists(temp_dir), \
                f"All temporary directories should be cleaned up: {temp_dir}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_temp_directory_deleted_even_on_exception(self, iterations):
        """
        Property 10: 临时目录生命周期 - 即使发生异常也删除临时目录
        
        For any execution of TempConfigManager that raises an exception,
        the temporary directory should still be deleted after the context
        manager exits.
        
        Validates: Requirement 4.3
        """
        for _ in range(iterations):
            temp_dir_path = None
            
            try:
                with TempConfigManager() as temp_dir:
                    temp_dir_path = temp_dir
                    assert os.path.exists(temp_dir), \
                        f"Directory should exist during context: {temp_dir}"
                    
                    # Simulate an exception
                    raise ValueError("Simulated exception for testing")
            except ValueError:
                # Expected exception, verify cleanup still happened
                pass
            
            # Verify directory was cleaned up despite exception
            assert temp_dir_path is not None, "temp_dir should have been set"
            assert not os.path.exists(temp_dir_path), \
                f"Directory should be deleted even after exception: {temp_dir_path}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_multiple_temp_directories_are_unique(self, iterations):
        """
        Property 10: 临时目录生命周期 - 多次创建的临时目录是唯一的
        
        For any multiple executions of TempConfigManager, each should
        create a unique temporary directory with different paths.
        
        Validates: Requirement 4.1
        """
        temp_dirs = []
        
        for _ in range(iterations):
            with TempConfigManager() as temp_dir:
                # Verify this directory is unique
                assert temp_dir not in temp_dirs, \
                    f"Each temporary directory should be unique, but {temp_dir} was created twice"
                
                temp_dirs.append(temp_dir)
                
                # Verify all directories have claude_ prefix
                dir_name = os.path.basename(temp_dir)
                assert dir_name.startswith("claude_"), \
                    f"Directory should have claude_ prefix: {dir_name}"
        
        # Verify all directories were cleaned up
        for temp_dir in temp_dirs:
            assert not os.path.exists(temp_dir), \
                f"All temporary directories should be cleaned up: {temp_dir}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_nested_context_managers_work_correctly(self, iterations):
        """
        Property 10: 临时目录生命周期 - 嵌套上下文管理器正确工作
        
        For any nested usage of TempConfigManager, each context should
        have its own temporary directory and environment variable state,
        and cleanup should happen in the correct order.
        
        Validates: Requirements 4.1, 4.2, 4.3
        """
        for _ in range(iterations):
            with TempConfigManager() as outer_temp_dir:
                outer_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
                
                # Verify outer context
                assert os.path.exists(outer_temp_dir), \
                    f"Outer directory should exist: {outer_temp_dir}"
                assert outer_config_dir == outer_temp_dir, \
                    f"Outer CLAUDE_CONFIG_DIR should match outer temp dir"
                
                with TempConfigManager() as inner_temp_dir:
                    inner_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
                    
                    # Verify inner context
                    assert os.path.exists(inner_temp_dir), \
                        f"Inner directory should exist: {inner_temp_dir}"
                    assert inner_config_dir == inner_temp_dir, \
                        f"Inner CLAUDE_CONFIG_DIR should match inner temp dir"
                    
                    # Verify inner and outer are different
                    assert inner_temp_dir != outer_temp_dir, \
                        "Inner and outer temp directories should be different"
                
                # After inner context exits, verify inner cleanup and outer restoration
                assert not os.path.exists(inner_temp_dir), \
                    f"Inner directory should be deleted: {inner_temp_dir}"
                
                current_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
                assert current_config_dir == outer_temp_dir, \
                    f"CLAUDE_CONFIG_DIR should be restored to outer temp dir after inner exit"
                
                assert os.path.exists(outer_temp_dir), \
                    f"Outer directory should still exist: {outer_temp_dir}"
            
            # After outer context exits, verify outer cleanup
            assert not os.path.exists(outer_temp_dir), \
                f"Outer directory should be deleted: {outer_temp_dir}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_temp_directory_is_writable(self, iterations):
        """
        Property 10: 临时目录生命周期 - 临时目录是可写的
        
        For any execution of TempConfigManager, the created temporary
        directory should be writable, allowing Claude Code to store
        configuration files.
        
        Validates: Requirement 4.1
        """
        for _ in range(iterations):
            with TempConfigManager() as temp_dir:
                # Try to create a test file in the directory
                test_file = os.path.join(temp_dir, "test_config.json")
                
                try:
                    with open(test_file, 'w') as f:
                        f.write('{"test": "data"}')
                    
                    # Verify file was created
                    assert os.path.exists(test_file), \
                        f"Should be able to create files in temp directory: {test_file}"
                    
                    # Verify file is readable
                    with open(test_file, 'r') as f:
                        content = f.read()
                        assert content == '{"test": "data"}', \
                            "Should be able to read files from temp directory"
                except (IOError, OSError) as e:
                    pytest.fail(f"Temporary directory should be writable: {e}")
            
            # Verify cleanup removed the file too
            assert not os.path.exists(test_file), \
                f"Test file should be deleted with temp directory: {test_file}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_environment_variable_restored_on_exception(self, iterations):
        """
        Property 10: 临时目录生命周期 - 异常时环境变量也被恢复
        
        For any execution of TempConfigManager that raises an exception,
        the CLAUDE_CONFIG_DIR environment variable should still be
        restored to its original state.
        
        Validates: Requirement 4.2
        """
        # Save original state
        original_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        
        for _ in range(iterations):
            try:
                with TempConfigManager() as temp_dir:
                    # Verify environment variable is set
                    assert os.environ.get("CLAUDE_CONFIG_DIR") == temp_dir, \
                        "CLAUDE_CONFIG_DIR should be set during context"
                    
                    # Simulate an exception
                    raise RuntimeError("Test exception")
            except RuntimeError:
                # Expected exception
                pass
            
            # Verify environment variable is restored
            current_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
            if original_config_dir is None:
                assert current_config_dir is None, \
                    f"CLAUDE_CONFIG_DIR should be removed after exception, but got: {current_config_dir}"
            else:
                assert current_config_dir == original_config_dir, \
                    f"CLAUDE_CONFIG_DIR should be restored after exception. Expected: {original_config_dir}, Got: {current_config_dir}"
        
        # Restore original state
        if original_config_dir is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = original_config_dir
    
    @settings(max_examples=100, deadline=None)
    @given(
        iterations=st.integers(min_value=1, max_value=5)
    )
    def test_temp_directory_cleanup_is_idempotent(self, iterations):
        """
        Property 10: 临时目录生命周期 - 临时目录清理是幂等的
        
        For any execution of TempConfigManager, calling cleanup multiple
        times on the same directory should not cause errors.
        
        Validates: Requirement 4.3
        """
        for _ in range(iterations):
            manager = TempConfigManager()
            temp_dir = manager.create_temp_dir()
            
            # Verify directory exists
            assert os.path.exists(temp_dir), \
                f"Directory should exist after creation: {temp_dir}"
            
            # First cleanup
            manager.cleanup(temp_dir)
            assert not os.path.exists(temp_dir), \
                f"Directory should be deleted after first cleanup: {temp_dir}"
            
            # Second cleanup should not raise an error
            try:
                manager.cleanup(temp_dir)
            except Exception as e:
                pytest.fail(f"Second cleanup should not raise an error: {e}")
            
            # Third cleanup should also not raise an error
            try:
                manager.cleanup(temp_dir)
            except Exception as e:
                pytest.fail(f"Third cleanup should not raise an error: {e}")
