"""ArXiv paper fetcher."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional
from xml.etree import ElementTree

import aiohttp
from bs4 import BeautifulSoup

from src.core.config import settings
from src.core.logger import get_logger
from src.database.models import Paper
from src.database.repositories import PaperRepository


logger = get_logger(__name__)


class ArxivFetcher:
    """Fetch papers from arXiv API."""

    # arXiv API configuration
    ARXIV_API_URL = "http://export.arxiv.org/api/query"

    # Topic-specific search queries
    TOPICS = {
        "llm_general": {
            "query": "cat:cs.CL AND (all:LLM OR all:GPT OR all:transformer OR all:prompt OR all:reasoning OR all:RAG OR all:retrieval)",
            "description": "LLM General - Prompt engineering, reasoning, RAG",
        },
        "llm_oil_gas": {
            "query": (
                "cat:cs.CL AND (all:LLM OR all:GPT OR all:transformer OR all:prompt) "
                "AND (all:oil OR all:gas OR all:geology OR all:geophysics OR all:petrophysics OR all:drilling OR all:hydraulic OR all:reservoir)"
            ),
            "description": "LLM in Oil & Gas",
        },
        "ai_oil_gas": {
            "query": (
                "cat:cs.CL AND (all:AI OR all:machine learning OR all:deep learning OR all:neural) "
                "AND (all:oil OR all:gas OR all:geology OR all:geophysics OR all:petrophysics OR all:drilling OR all:reservoir)"
            ),
            "description": "AI in Oil & Gas",
        },
    }

    def __init__(self, max_results: int = 500, sort_by: str = "submittedDate"):
        self.max_results = max_results
        self.sort_by = sort_by
        self.session = aiohttp.ClientSession()

    async def fetch_papers(
        self,
        topic: str,
        days_back: int = 1,
        start_from: Optional[datetime] = None,
    ) -> list[dict]:
        """Fetch papers for a specific topic.

        Args:
            topic: Topic key (llm_general, llm_oil_gas, ai_oil_gas)
            days_back: Number of days to look back
            start_from: Custom start date

        Returns:
            List of paper dictionaries
        """
        if topic not in self.TOPICS:
            raise ValueError(f"Unknown topic: {topic}")

        if start_from is None:
            start_from = datetime.now() - timedelta(days=days_back)

        # Build arXiv query
        topic_config = self.TOPICS[topic]
        query = f"{topic_config['query']} AND submittedDate:[{start_from.strftime('%Y%m%d')} TO {datetime.now().strftime('%Y%m%d')}]"

        params = {
            "search_query": query,
            "start": 0,
            "max_results": self.max_results,
            "sortBy": self.sort_by,
            "sortOrder": "descending",
        }

        logger.info(f"Fetching papers from arXiv for topic: {topic}")
        logger.debug(f"Query: {query}")

        try:
            async with self.session.get(self.ARXIV_API_URL, params=params) as response:
                response.raise_for_status()
                data = await response.text()

            # Parse arXiv XML response
            papers = self._parse_arxiv_response(data, topic)
            logger.info(f"Fetched {len(papers)} papers for topic {topic}")
            return papers

        except aiohttp.ClientError as e:
            logger.error(f"arXiv API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            raise

    def _parse_arxiv_response(self, xml_data: str, topic: str) -> list[dict]:
        """Parse arXiv XML response into paper dictionaries."""
        papers = []

        try:
            root = ElementTree.fromstring(xml_data)

            # arXiv uses Atom namespace
            namespace = {"atom": "http://www.w3.org/2005/Atom"}

            entries = root.findall("atom:entry", namespace)

            for entry in entries:
                paper = self._parse_entry(entry, namespace, topic)
                if paper:
                    papers.append(paper)

            return papers
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            return []

    def _parse_entry(self, entry, namespace: dict, topic: str) -> Optional[dict]:
        """Parse single arXiv entry."""
        try:
            # Extract basic fields
            arxiv_id_elem = entry.find("atom:id", namespace)
            if arxiv_id_elem is None:
                return None

            arxiv_url = arxiv_id_elem.text
            arxiv_id = self._extract_arxiv_id(arxiv_url)

            if not arxiv_id:
                return None

            # Title
            title_elem = entry.find("atom:title", namespace)
            title = title_elem.text if title_elem is not None else ""

            # Abstract
            abstract_elem = entry.find("atom:summary", namespace)
            abstract = abstract_elem.text if abstract_elem is not None else ""

            # Authors
            authors = []
            for author in entry.findall("atom:author", namespace):
                name_elem = author.find("atom:name", namespace)
                if name_elem is not None:
                    authors.append(name_elem.text)

            # Published date
            published_elem = entry.find("atom:published", namespace)
            published_date = None
            if published_elem is not None:
                try:
                    published_date = datetime.strptime(published_elem.text, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass

            # PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            return {
                "arxiv_id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published_date": published_date,
                "arxiv_url": arxiv_url,
                "pdf_url": pdf_url,
                "topic": topic,
            }
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None

    def _extract_arxiv_id(self, url: str) -> Optional[str]:
        # URLs are like: http://arxiv.org/abs/2301.12345v1
        match = re.search(r"arxiv\.org/abs/(\d+\.\d+v?\d+)", url)
        if match:
            return match.group(1)
        return None

    async def fetch_full_text(self, pdf_url: str) -> Optional[str]:
        # TODO: Implement PDF text extraction
        # This would require:
        # 1. Download PDF
        # 2. Extract text using PyMuPDF or similar
        # 3. Clean and format text
        logger.warning("Full text extraction not yet implemented")
        return None

    async def close(self):
        """Close aiohttp session."""
        await self.session.close()
