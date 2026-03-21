# -*- coding: utf-8 -*-
"""飞书云文档工具

提供飞书云文档的读取、创建、修改等操作
"""
from typing import Dict, Any, Optional, List
from agentscope.tool import ToolResponse
from agentscope.message import TextBlock

# 全局飞书客户端实例
_lark_client = None


def _get_lark_client():
    """获取或创建飞书客户端单例"""
    global _lark_client
    if _lark_client is None:
        from ...config import BotConfig
        config = BotConfig.from_env()
        from lark_oapi import Client as LarkClient
        _lark_client = LarkClient.builder()\
            .app_id(config.app_id)\
            .app_secret(config.app_secret)\
            .build()
    return _lark_client


def _extract_doc_token(doc_identifier: str) -> str:
    """从文档标识中提取 doc_token
    
    Args:
        doc_identifier: 文档URL或直接的doc_token
        
    Returns:
        str: 提取的doc_token
    """
    import re
    
    # 清理输入，移除反引号、空格等
    doc_identifier = doc_identifier.strip().strip('`').strip()
    
    # 从URL中提取 - 支持多种飞书文档URL格式
    # 格式1: https://xxx.feishu.cn/wiki/TOKEN
    # 格式2: https://xxx.feishu.cn/docx/TOKEN
    # 格式3: https://xxx.larksuite.com/wiki/TOKEN
    url_patterns = [
        r'wiki/([\w]+)',  # wiki格式
        r'docx/([\w]+)',  # docx格式
        r'docs/([\w]+)',  # docs格式
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, doc_identifier)
        if match:
            return match.group(1)
    
    # 如果输入是直接的token（没有URL路径），直接返回
    # 移除任何可能的特殊字符
    clean_token = re.sub(r'[^\w]', '', doc_identifier)
    if clean_token:
        return clean_token
    
    return doc_identifier


async def feishu_doc_read_markdown(doc_token: str, lang: str = "zh") -> ToolResponse:
    """获取飞书文档的Markdown格式内容
    
    Args:
        doc_token: 文档标识或URL
        lang: 语言，默认为"zh"
        
    Returns:
        ToolResponse: 包含Markdown内容的响应
    """
    try:
        from lark_oapi.api.docx.v1 import RawContentDocumentRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        request = RawContentDocumentRequest.builder()\
            .document_id(doc_token)\
            .build()
        
        response = client.docx.v1.document.raw_content(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"读取文档失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        # 检查响应数据
        if response.data is None:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="读取文档失败: 响应数据为空"
                    ),
                ],
            )
        
        # 获取内容
        content = getattr(response.data, 'content', None)
        if content is None:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="读取文档失败: 文档内容为空"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=content
                ),
            ],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"读取文档失败: {str(e)}\n详细错误:\n{error_detail}"
                ),
            ],
        )


async def feishu_doc_read_blocks(doc_token: str, document_revision_id: int = -1, user_id_type: str = "open_id") -> ToolResponse:
    """获取飞书文档的块结构数据
    
    Args:
        doc_token: 文档标识或URL
        document_revision_id: 文档版本ID，默认为-1（最新版本）
        user_id_type: 用户ID类型，默认为"open_id"
        
    Returns:
        ToolResponse: 包含块结构数据的响应
    """
    try:
        from lark_oapi.api.docx.v1 import GetDocumentBlockChildrenRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        # 使用文档ID作为根块ID来获取所有子块
        request = GetDocumentBlockChildrenRequest.builder()\
            .document_id(doc_token)\
            .document_revision_id(document_revision_id)\
            .build()
        
        response = client.docx.v1.document_block.children(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"读取文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        # 将块数据转换为文本格式
        blocks_text = []
        items = getattr(response.data, 'items', [])
        
        for block in items:
            block_type = getattr(block, 'block_type', 'unknown')
            block_id = getattr(block, 'block_id', 'unknown')
            blocks_text.append(f"块ID: {block_id}, 类型: {block_type}")
        
        if not blocks_text:
            result_text = "文档为空或无法读取块结构"
        else:
            result_text = "\n".join(blocks_text)
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"文档块数据:\n{result_text}"
                ),
            ],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"读取文档块失败: {str(e)}\n详细错误:\n{error_detail}"
                ),
            ],
        )


async def feishu_doc_read_raw(doc_token: str, lang: str = "zh") -> ToolResponse:
    """获取飞书文档的纯文本内容
    
    Args:
        doc_token: 文档标识或URL
        lang: 语言，默认为"zh"
        
    Returns:
        ToolResponse: 包含纯文本内容的响应
    """
    try:
        from lark_oapi.api.docx.v1 import RawContentDocumentRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        request = RawContentDocumentRequest.builder()\
            .document_id(doc_token)\
            .build()
        
        response = client.docx.v1.document.raw_content(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"读取文档纯文本失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        # 检查响应数据
        if response.data is None:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="读取文档纯文本失败: 响应数据为空"
                    ),
                ],
            )
        
        # 获取内容
        content = getattr(response.data, 'content', None)
        if content is None:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="读取文档纯文本失败: 文档内容为空"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=content
                ),
            ],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"读取文档纯文本失败: {str(e)}\n详细错误:\n{error_detail}"
                ),
            ],
        )


async def feishu_doc_get_info(doc_token: str) -> ToolResponse:
    """获取飞书文档的基本信息
    
    Args:
        doc_token: 文档标识或URL
        
    Returns:
        ToolResponse: 包含文档信息的响应
    """
    try:
        from lark_oapi.api.docx.v1 import GetDocumentRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        request = GetDocumentRequest.builder()\
            .document_id(doc_token)\
            .build()
        
        response = client.docx.v1.document.get(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"获取文档信息失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        # 检查响应数据
        if response.data is None:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text="获取文档信息失败: 响应数据为空"
                    ),
                ],
            )
        
        # 安全获取属性
        title = getattr(response.data, 'title', 'N/A')
        document_id = getattr(response.data, 'document_id', 'N/A')
        created_at = getattr(response.data, 'created_at', 'N/A')
        updated_at = getattr(response.data, 'updated_at', 'N/A')
        
        info_text = f"""文档信息:
标题: {title}
文档ID: {document_id}
创建时间: {created_at}
更新时间: {updated_at}
"""
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=info_text
                ),
            ],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"获取文档信息失败: {str(e)}\n详细错误:\n{error_detail}"
                ),
            ],
        )


async def feishu_doc_create(title: str, folder_token: Optional[str] = None) -> ToolResponse:
    """创建新的飞书文档
    
    Args:
        title: 文档标题
        folder_token: 文件夹标识，可选
        
    Returns:
        ToolResponse: 包含创建结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import CreateDocumentRequest
        
        client = _get_lark_client()
        
        # 直接创建请求对象并设置属性
        request = CreateDocumentRequest.builder().build()
        if title:
            request.title = title
        if folder_token:
            request.folder_token = folder_token
        
        response = client.docx.v1.document.create(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"创建文档失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        # 设置文档权限为公开，避免用户需要申请权限
        try:
            from lark_oapi.api.drive.v1 import PatchPermissionPublicRequest, PermissionPublicRequest
            
            document_id = response.data.document.document_id
            
            # 创建权限请求对象
            permission_body = PermissionPublicRequest()
            permission_body.external_access = True
            permission_body.share_entity = "tenant"
            
            # 创建更新请求 - 使用 builder 来正确设置 uri 和 paths
            permission_request = PatchPermissionPublicRequest.builder()\
                .token(document_id)\
                .request_body(permission_body)\
                .build()
            
            # 直接调用客户端方法
            permission_response = client.drive.v1.permission_public.patch(permission_request)
            
            if not permission_response.success():
                print(f"设置文档权限失败: {permission_response.code} - {permission_response.msg}")
            else:
                print("文档权限设置成功：已设置为公开访问")
        except Exception as perm_error:
            print(f"设置文档权限异常: {str(perm_error)}")
            import traceback
            traceback.print_exc()
        
        result_text = f"""文档创建成功:
标题: {response.data.document.title}
文档ID: {response.data.document.document_id}
"""
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=result_text
                ),
            ],
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"创建文档失败: {str(e)}\n详细错误:\n{error_detail}"
                ),
            ],
        )


async def feishu_doc_convert_markdown_to_blocks(markdown_content: str) -> ToolResponse:
    """将Markdown内容转换为文档块
    
    Args:
        markdown_content: Markdown格式的内容
        
    Returns:
        ToolResponse: 包含转换结果的响应
    """
    try:
        # 这里简化处理，实际需要调用飞书的转换API
        # 暂时返回模拟数据
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"Markdown转换结果:\n{markdown_content}"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"转换Markdown失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_create_block(doc_token: str, parent_block_id: str, block_data: Dict[str, Any], index: int = 0) -> ToolResponse:
    """创建文档块
    
    Args:
        doc_token: 文档标识或URL
        parent_block_id: 父块ID
        block_data: 块数据
        index: 插入位置，默认为0
        
    Returns:
        ToolResponse: 包含创建结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import CreateDocumentBlockChildrenRequest
        from lark_oapi.api.docx.v1.model import TextElement
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        builder = CreateDocumentBlockChildrenRequest.builder()\
            .document_id(doc_token)\
            .index(index)
        
        if parent_block_id:
            builder.block_id(parent_block_id)
        else:
            builder.block_id(doc_token)
        
        # 构建块数据
        if block_data.get("type") == "text":
            text_element = TextElement.builder()\
                .text(block_data.get("text", ""))\
                .build()
            builder.children([text_element])
        
        request = builder.build()
        response = client.docx.v1.document_block.children(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"创建文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        result_text = f"""文档块创建成功:
块ID: {response.data.items[0].block_id}
"""
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=result_text
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"创建文档块失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_update_block(doc_token: str, block_id: str, block_data: Dict[str, Any]) -> ToolResponse:
    """更新文档块
    
    Args:
        doc_token: 文档标识或URL
        block_id: 块ID
        block_data: 块数据
        
    Returns:
        ToolResponse: 包含更新结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import UpdateBlockRequest
        from lark_oapi.api.docx.v1.model import TextElement
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        builder = UpdateBlockRequest.builder()\
            .document_id(doc_token)\
            .block_id(block_id)
        
        # 构建块数据
        if block_data.get("type") == "text":
            text_element = TextElement.builder()\
                .text(block_data.get("text", ""))\
                .build()
            builder.children([text_element])
        
        request = builder.build()
        response = client.docx.v1.document_block.update(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"更新文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text="文档块更新成功"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"更新文档块失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_delete_block(doc_token: str, block_id: str) -> ToolResponse:
    """删除文档块
    
    Args:
        doc_token: 文档标识或URL
        block_id: 块ID
        
    Returns:
        ToolResponse: 包含删除结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import BatchDeleteDocumentBlockChildrenRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        request = BatchDeleteDocumentBlockChildrenRequest.builder()\
            .document_id(doc_token)\
            .block_id(block_id)\
            .children([block_id])\
            .build()
        
        response = client.docx.v1.document_block.children(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"删除文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text="文档块删除成功"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"删除文档块失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_batch_update_blocks(doc_token: str, blocks: List[Dict[str, Any]]) -> ToolResponse:
    """批量更新文档块
    
    Args:
        doc_token: 文档标识或URL
        blocks: 块数据列表，每个元素包含block_id和data
        
    Returns:
        ToolResponse: 包含批量更新结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import BatchUpdateDocumentBlockRequest
        from lark_oapi.api.docx.v1.model import TextElement
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        builder = BatchUpdateDocumentBlockRequest.builder()\
            .document_id(doc_token)
        
        # 构建块数据列表
        update_blocks = []
        
        for block_item in blocks:
            if block_item["data"].get("type") == "text":
                text_element = TextElement.builder()\
                    .text(block_item["data"].get("text", ""))\
                    .build()
                update_blocks.append(text_element)
        
        builder.children(update_blocks)
        
        request = builder.build()
        response = client.docx.v1.document_block.batch_update(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"批量更新文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"批量更新文档块成功，共更新 {len(blocks)} 个块"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"批量更新文档块失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_batch_delete_blocks(doc_token: str, block_ids: List[str]) -> ToolResponse:
    """批量删除文档块
    
    Args:
        doc_token: 文档标识或URL
        block_ids: 块ID列表
        
    Returns:
        ToolResponse: 包含批量删除结果的响应
    """
    try:
        from lark_oapi.api.docx.v1 import BatchDeleteDocumentBlockChildrenRequest
        
        client = _get_lark_client()
        doc_token = _extract_doc_token(doc_token)
        
        request = BatchDeleteDocumentBlockChildrenRequest.builder()\
            .document_id(doc_token)\
            .block_id(doc_token)\
            .children(block_ids)\
            .build()
        
        response = client.docx.v1.document_block.children(request)
        
        if not response.success():
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"批量删除文档块失败: {response.code} - {response.msg}"
                    ),
                ],
            )
        
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"批量删除文档块成功，共删除 {len(block_ids)} 个块"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"批量删除文档块失败: {str(e)}"
                ),
            ],
        )


async def feishu_doc_list(page_size: int = 20, page_token: str = "") -> ToolResponse:
    """获取飞书文档列表
    
    Args:
        page_size: 每页大小，默认为20
        page_token: 分页标记，默认为空
        
    Returns:
        ToolResponse: 包含文档列表的响应
    """
    try:
        # 飞书API可能不直接提供文档列表功能
        # 这里返回模拟数据
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text="文档列表功能需要使用搜索API或从其他来源获取"
                ),
            ],
        )
    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"获取文档列表失败: {str(e)}"
                ),
            ],
        )
