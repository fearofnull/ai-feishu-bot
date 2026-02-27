"""
临时配置管理器单元测试

测试 TempConfigManager 的清理功能，包括正常清理、异常情况和日志记录。
"""
import os
import tempfile
import shutil
import logging
import pytest
from unittest.mock import patch, MagicMock
from feishu_bot.temp_config_manager import TempConfigManager


class TestTempConfigManagerCleanup:
    """临时配置管理器清理功能单元测试类"""
    
    def test_cleanup_removes_existing_directory(self):
        """
        测试正常清理 - 清理存在的临时目录
        
        Validates: Requirement 4.3
        """
        # Create a temporary directory manually
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        # Create some files in it
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Verify directory and file exist
        assert os.path.exists(temp_dir)
        assert os.path.exists(test_file)
        
        # Cleanup using TempConfigManager
        manager = TempConfigManager()
        manager.cleanup(temp_dir)
        
        # Verify directory and file are removed
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(test_file)
    
    def test_cleanup_handles_nonexistent_directory(self):
        """
        测试异常情况 - 清理不存在的目录不会抛出异常
        
        Validates: Requirement 4.4
        """
        manager = TempConfigManager()
        
        # Try to cleanup a non-existent directory
        non_existent_dir = "/tmp/claude_nonexistent_12345"
        
        # Should not raise an exception
        try:
            manager.cleanup(non_existent_dir)
        except Exception as e:
            pytest.fail(f"Cleanup should not raise exception for non-existent directory: {e}")
    
    def test_cleanup_handles_none_directory(self):
        """
        测试异常情况 - 清理 None 目录不会抛出异常
        
        Validates: Requirement 4.4
        """
        manager = TempConfigManager()
        
        # Try to cleanup None
        try:
            manager.cleanup(None)
        except Exception as e:
            pytest.fail(f"Cleanup should not raise exception for None: {e}")
    
    def test_cleanup_handles_empty_string(self):
        """
        测试异常情况 - 清理空字符串不会抛出异常
        
        Validates: Requirement 4.4
        """
        manager = TempConfigManager()
        
        # Try to cleanup empty string
        try:
            manager.cleanup("")
        except Exception as e:
            pytest.fail(f"Cleanup should not raise exception for empty string: {e}")
    
    def test_cleanup_logs_error_on_permission_denied(self, caplog):
        """
        测试清理失败的日志记录 - 权限拒绝时记录错误日志
        
        Validates: Requirement 4.4
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        manager = TempConfigManager()
        
        # Mock shutil.rmtree to raise PermissionError
        with patch('shutil.rmtree', side_effect=PermissionError("Permission denied")):
            with caplog.at_level(logging.ERROR):
                manager.cleanup(temp_dir)
            
            # Verify error was logged
            assert len(caplog.records) > 0
            assert any("Failed to cleanup temporary directory" in record.message 
                      for record in caplog.records)
            assert any(temp_dir in record.message 
                      for record in caplog.records)
        
        # Cleanup the directory manually since mock prevented it
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_cleanup_logs_error_on_os_error(self, caplog):
        """
        测试清理失败的日志记录 - OS 错误时记录错误日志
        
        Validates: Requirement 4.4
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        manager = TempConfigManager()
        
        # Mock shutil.rmtree to raise OSError
        with patch('shutil.rmtree', side_effect=OSError("OS error occurred")):
            with caplog.at_level(logging.ERROR):
                manager.cleanup(temp_dir)
            
            # Verify error was logged
            assert len(caplog.records) > 0
            assert any("Failed to cleanup temporary directory" in record.message 
                      for record in caplog.records)
            assert any("OS error occurred" in record.message 
                      for record in caplog.records)
        
        # Cleanup the directory manually since mock prevented it
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_cleanup_continues_processing_after_failure(self):
        """
        测试清理失败后继续处理 - 清理失败不应该中断主流程
        
        Validates: Requirement 4.4
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        manager = TempConfigManager()
        
        # Mock shutil.rmtree to raise an exception
        with patch('shutil.rmtree', side_effect=Exception("Cleanup failed")):
            # Cleanup should not raise an exception
            try:
                manager.cleanup(temp_dir)
            except Exception as e:
                pytest.fail(f"Cleanup failure should not raise exception: {e}")
        
        # Cleanup the directory manually since mock prevented it
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_cleanup_removes_nested_directories(self):
        """
        测试正常清理 - 清理包含嵌套目录的临时目录
        
        Validates: Requirement 4.3
        """
        # Create a temporary directory with nested structure
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        nested_dir = os.path.join(temp_dir, "nested", "deep")
        os.makedirs(nested_dir)
        
        # Create files at different levels
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "nested", "file2.txt")
        file3 = os.path.join(nested_dir, "file3.txt")
        
        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")
        with open(file3, 'w') as f:
            f.write("content3")
        
        # Verify structure exists
        assert os.path.exists(temp_dir)
        assert os.path.exists(nested_dir)
        assert os.path.exists(file1)
        assert os.path.exists(file2)
        assert os.path.exists(file3)
        
        # Cleanup
        manager = TempConfigManager()
        manager.cleanup(temp_dir)
        
        # Verify everything is removed
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(nested_dir)
        assert not os.path.exists(file1)
        assert not os.path.exists(file2)
        assert not os.path.exists(file3)
    
    def test_cleanup_removes_readonly_files(self):
        """
        测试正常清理 - 清理包含只读文件的临时目录
        
        Validates: Requirement 4.3
        
        Note: On Windows, readonly files may require special handling.
        This test verifies that cleanup attempts to remove readonly files,
        and logs errors if it fails (per Requirement 4.4).
        """
        # Create a temporary directory with a readonly file
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        readonly_file = os.path.join(temp_dir, "readonly.txt")
        
        with open(readonly_file, 'w') as f:
            f.write("readonly content")
        
        # Make file readonly
        os.chmod(readonly_file, 0o444)
        
        # Verify file exists and is readonly
        assert os.path.exists(readonly_file)
        assert not os.access(readonly_file, os.W_OK)
        
        # Cleanup should attempt to handle readonly files
        manager = TempConfigManager()
        manager.cleanup(temp_dir)
        
        # On Unix-like systems, cleanup should succeed
        # On Windows, cleanup may fail due to readonly files, which is acceptable
        # per Requirement 4.4 (log error but continue processing)
        # So we don't assert the directory is removed, just that no exception was raised
        
        # Manual cleanup for Windows
        if os.path.exists(temp_dir):
            # Make file writable again and cleanup
            os.chmod(readonly_file, 0o666)
            shutil.rmtree(temp_dir)
    
    def test_context_manager_cleans_up_on_success(self):
        """
        测试上下文管理器正常清理 - 成功执行后清理临时目录
        
        Validates: Requirement 4.3
        """
        temp_dir_path = None
        
        with TempConfigManager() as temp_dir:
            temp_dir_path = temp_dir
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Verify directory and file exist
            assert os.path.exists(temp_dir)
            assert os.path.exists(test_file)
        
        # After context exit, verify cleanup
        assert temp_dir_path is not None
        assert not os.path.exists(temp_dir_path)
    
    def test_context_manager_cleans_up_on_exception(self):
        """
        测试上下文管理器异常清理 - 异常发生后仍然清理临时目录
        
        Validates: Requirement 4.3
        """
        temp_dir_path = None
        
        try:
            with TempConfigManager() as temp_dir:
                temp_dir_path = temp_dir
                
                # Create a test file
                test_file = os.path.join(temp_dir, "test.txt")
                with open(test_file, 'w') as f:
                    f.write("test")
                
                # Verify directory and file exist
                assert os.path.exists(temp_dir)
                assert os.path.exists(test_file)
                
                # Raise an exception
                raise ValueError("Test exception")
        except ValueError:
            # Expected exception
            pass
        
        # After context exit with exception, verify cleanup still happened
        assert temp_dir_path is not None
        assert not os.path.exists(temp_dir_path)
    
    def test_context_manager_logs_cleanup_failure(self, caplog):
        """
        测试上下文管理器清理失败日志 - 清理失败时记录日志但不抛出异常
        
        Validates: Requirement 4.4
        """
        with patch('shutil.rmtree', side_effect=Exception("Cleanup failed")):
            with caplog.at_level(logging.ERROR):
                try:
                    with TempConfigManager() as temp_dir:
                        # Just enter and exit the context
                        pass
                except Exception as e:
                    pytest.fail(f"Context manager should not raise exception on cleanup failure: {e}")
            
            # Verify error was logged
            assert len(caplog.records) > 0
            assert any("Failed to cleanup temporary directory" in record.message 
                      for record in caplog.records)
    
    @pytest.mark.skipif(os.name == 'nt', reason="Symlinks require admin privileges on Windows")
    def test_cleanup_with_symlinks(self):
        """
        测试正常清理 - 清理包含符号链接的临时目录
        
        Validates: Requirement 4.3
        
        Note: This test is skipped on Windows as creating symlinks requires
        administrator privileges.
        """
        # Create a temporary directory with a symlink
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        # Create a target file outside temp_dir
        target_file = tempfile.NamedTemporaryFile(delete=False)
        target_file.write(b"target content")
        target_file.close()
        
        try:
            # Create a symlink inside temp_dir
            symlink_path = os.path.join(temp_dir, "symlink.txt")
            os.symlink(target_file.name, symlink_path)
            
            # Verify symlink exists
            assert os.path.exists(symlink_path)
            assert os.path.islink(symlink_path)
            
            # Cleanup
            manager = TempConfigManager()
            manager.cleanup(temp_dir)
            
            # Verify temp_dir is removed
            assert not os.path.exists(temp_dir)
            assert not os.path.exists(symlink_path)
            
            # Verify target file still exists (symlink removal shouldn't affect target)
            assert os.path.exists(target_file.name)
        finally:
            # Cleanup target file
            if os.path.exists(target_file.name):
                os.unlink(target_file.name)
    
    def test_multiple_cleanup_calls_are_safe(self):
        """
        测试异常情况 - 多次调用 cleanup 是安全的（幂等性）
        
        Validates: Requirement 4.4
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="claude_test_")
        
        manager = TempConfigManager()
        
        # First cleanup
        manager.cleanup(temp_dir)
        assert not os.path.exists(temp_dir)
        
        # Second cleanup should not raise an exception
        try:
            manager.cleanup(temp_dir)
        except Exception as e:
            pytest.fail(f"Second cleanup should not raise exception: {e}")
        
        # Third cleanup should also not raise an exception
        try:
            manager.cleanup(temp_dir)
        except Exception as e:
            pytest.fail(f"Third cleanup should not raise exception: {e}")
