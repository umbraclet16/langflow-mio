from __future__ import annotations

import os
from typing import Any

import httpx

from lfx.custom import Component
from lfx.io import DropdownInput, FloatInput, IntInput, MessageTextInput, Output
from lfx.schema.data import Data
from lfx.schema.dataframe import DataFrame

_SEARCH_MODE_MAP: dict[str, str] = {
    "向量检索": "embedding",
    "全文检索": "keywords",
    "混合检索": "blend",
}


class ExternalKnowledgeBaseComponent(Component):
    display_name = "外部知识库"
    description = "使用智能体平台的知识库检索API进行知识库检索"
    icon = "database"
    name = "ExternalKnowledgeBase"

    inputs = [
        MessageTextInput(
            name="kb_id",
            display_name="知识库ID",
            info="The ID of the knowledge base to query.",
            required=True,
        ),
        MessageTextInput(
            name="query_text",
            display_name="检索内容",
            info="The search query to retrieve from the knowledge base.",
            tool_mode=True,
        ),
        DropdownInput(
            name="search_mode",
            display_name="检索模式",
            info="The retrieval mode for the query.",
            options=["向量检索", "全文检索", "混合检索"],
            value="hybrid",
            required=True,
        ),
        IntInput(
            name="top_number",
            display_name="返回条数",
            info="Number of top results to return.",
            value=5,
            required=True,
        ),
        FloatInput(
            name="similarity",
            display_name="相似度阈值",
            info="Minimum similarity score (0.0 to 1.0) for results.",
            value=0.3,
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="results",
            display_name="Results",
            method="query_knowledge_base",
            info="Retrieved documents from the external knowledge base.",
        ),
    ]

    async def query_knowledge_base(self) -> DataFrame:
        kb_id = self.kb_id
        query_text = self.query_text or ""
        search_mode = _SEARCH_MODE_MAP.get(self.search_mode, "embedding")
        top_number = self.top_number
        similarity = self.similarity
        api_base_url = os.environ.get("AGENT_PLATFORM_API_URL", "http://localhost:8000/v1").rstrip("/")
        url = f"{api_base_url}/maxkb/knowledge-bases/{kb_id}/query"

        payload: dict[str, Any] = {
            "query_text": query_text,
            "search_mode": search_mode,
            "top_number": top_number,
            "similarity": similarity,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result_data = response.json()
        except httpx.HTTPStatusError as e:
            msg = f"API returned error {e.response.status_code}: {e.response.text}"
            raise ValueError(msg) from e
        except httpx.RequestError as e:
            msg = f"Failed to connect to API at {url}: {e}"
            raise ValueError(msg) from e

        records = result_data.get("results") if isinstance(result_data, dict) else result_data
        if not records:
            self.log(f"No results retrieved from knowledge base {kb_id}")
            return DataFrame()

        data_list: list[Data] = []
        for record in records:
            content = record.get("content", "")
            data_list.append(
                Data(
                    content=content,
                    data={
                        "title": record.get("title", ""),
                        "document_name": record.get("document_name", ""),
                        "knowledge_name": record.get("knowledge_name", ""),
                        "similarity": record.get("similarity", 0.0),
                        "comprehensive_score": record.get("comprehensive_score", 0.0),
                        "document_id": record.get("document_id", ""),
                        "knowledge_id": record.get("knowledge_id", ""),
                        "hit_num": record.get("hit_num", 0),
                    },
                )
            )

        self.log(f"Retrieved {len(data_list)} results from knowledge base {kb_id}")
        return DataFrame(data=data_list)
