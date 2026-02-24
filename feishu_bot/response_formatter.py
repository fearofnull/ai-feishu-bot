"""
响应格式化器

格式化 AI 响应消息，确保消息格式清晰易读。
"""
from typing import Optional


class ResponseFormatter:
    """响应格式化器
    
    格式化 AI 执行结果为用户友好的消息格式。
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    
    def format_response(
        self,
        user_message: str,
        ai_output: str,
        error: Optional[str] = None
    ) -> str:
        """格式化响应消息
        
        Args:
            user_message: 用户原始消息
            ai_output: AI 输出内容
            error: 错误信息（可选）
            
        Returns:
            格式化后的响应消息
        """
        if error:
            return self.format_error(user_message, error)
        
        # 成功响应格式
        # 直接返回 AI 输出，不添加额外的格式化
        return ai_output
    
    def format_error(self, user_message: str, error_message: str) -> str:
        """格式化错误消息
        
        Args:
            user_message: 用户原始消息
            error_message: 错误信息
            
        Returns:
            格式化后的错误消息
        """
        return f"❌ 处理失败 / Error\n\n{error_message}"
